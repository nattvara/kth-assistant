from os.path import basename
import asyncio
import socket
import sys

from starlette.responses import Response
from uvicorn import Config, Server
from fastapi import FastAPI
import arrow

from services.llm.supported_models import get_enum_from_enum_name, LLMModel, EMBEDDING_MODELS
from llms.openai import load_openai_sdk, generate_text_streaming, compute_embedding
from llms.embeddings import load_hf_embedding_model
from cache.redis import get_redis_connection
from services.llm.llm import LLMService
from services.llm.worker import Worker
import config.settings as settings
from config.logger import log


def print_help():
    help_message = f"""
Usage: {basename(sys.argv[0])} MODEL_NAME DEVICE

This program starts a worker for a given model.

Running the program with DEVICE=download-only will just download the model, not start the worker.

Arguments:
    MODEL_NAME    The name of the model to run (e.g., MISTRAL_7B_INSTRUCT).
    DEVICE        The device to load the model onto (cpu|cuda|mps|download-only)

Example:
    {basename(sys.argv[0])} MISTRAL_7B_INSTRUCT cuda
"""
    print(help_message)


class ServerWithCustomShutdown(Server):

    async def shutdown(self, sockets: list[socket.socket] | None = None) -> None:
        log().info("Server shutdown started.")
        healthcheck._is_shutting_down = True
        healthcheck._worker.stop()
        healthcheck._shutdown_started_at = arrow.now()

        wait_time = settings.get_settings().LLM_WORKER_SHUTDOWN_DELAY_SECONDS
        log().info(f"Waiting {wait_time} seconds before terminating the healthcheck.")
        await asyncio.sleep(wait_time)

        log().info("Proceeding with actual server shutdown.")
        await super().shutdown(sockets)


healthcheck = FastAPI()
healthcheck._is_shutting_down = False
healthcheck._shutdown_started_at = None


@healthcheck.get("/", response_class=Response)
def index():
    if not healthcheck._is_shutting_down:
        log().debug("healthcheck ok.")
        return Response(content="I'm alive.", status_code=200, media_type="text/plain")
    else:
        wait_time = settings.get_settings().LLM_WORKER_SHUTDOWN_DELAY_SECONDS
        time_spent = (arrow.now() - healthcheck._shutdown_started_at).seconds
        log().debug(f"Healthcheck not ok, is in shutdown mode, {wait_time - time_spent} seconds left"
                    f" before terminating the healthcheck.")
        return Response(content="Server is shutting down.", status_code=503, media_type="text/plain")


@healthcheck.on_event("shutdown")
async def shutdown_event():
    healthcheck._worker.stop()  # noqa


async def _start_health_check_endpoint():
    try:
        port = await _find_available_port()
    except OSError as e:
        log().error(f"Error finding available port: {e}")
        exit(1)

    log().info(f"Using port {port} for health check endpoint")

    config = Config(app=healthcheck, host="0.0.0.0", port=port, loop="asyncio")
    server = ServerWithCustomShutdown(config)
    await server.serve()


async def _find_available_port(start_port: int = 1337):
    for port in range(start_port, 65535):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            pass
    raise OSError("No available port found")


async def worker_main():
    if len(sys.argv) != 3 or sys.argv[1] in ['-h', '--help']:
        print_help()
        exit(1)

    enum_name = sys.argv[1]
    try:
        model_enum = get_enum_from_enum_name(enum_name)
    except KeyError:
        print("Invalid model name")
        exit(1)

    download_only = False
    if sys.argv[2] == 'download-only':
        download_only = True

    log().info("Starting worker")

    service = LLMService(model_enum, await get_redis_connection())

    if model_enum in EMBEDDING_MODELS and model_enum is not LLMModel.OPENAI_TEXT_EMBEDDING_3_LARGE:
        worker = Worker(
            service,
            model_enum,
            device='cpu',
            model_loader_func=load_hf_embedding_model,
        )
    elif model_enum is LLMModel.OPENAI_TEXT_EMBEDDING_3_LARGE:
        worker = Worker(
            service,
            model_enum,
            device='python-api',
            model_loader_func=load_openai_sdk,
            embedding_function=compute_embedding
        )
    elif model_enum is not LLMModel.OPENAI_GPT4:
        if not download_only:
            device_name = sys.argv[2]
        else:
            device_name = 'cpu'

        worker = Worker(service, model_enum, device=device_name)
    else:
        worker = Worker(
            service,
            model_enum,
            device='python-api',
            model_loader_func=load_openai_sdk,
            text_generator=generate_text_streaming
        )

    if download_only:
        log().info("agent is running in 'download-only' mode, exiting.")
        return

    healthcheck._worker = worker
    await worker.run()

    log().info("worker terminated.")


async def _run_worker_main_with_healthcheck():
    task1 = asyncio.create_task(_start_health_check_endpoint())
    task2 = asyncio.create_task(worker_main())
    await asyncio.gather(task1, task2)


async def main():
    tasks = [asyncio.create_task(_start_health_check_endpoint()), asyncio.create_task(worker_main())]
    await asyncio.gather(*tasks)


def sync_main():
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
