from os.path import basename
import asyncio
import signal
import socket
import sys

from uvicorn import Config, Server
from fastapi import FastAPI

from services.llm.supported_models import get_enum_from_enum_name, LLMModel, EMBEDDING_MODELS
from llms.openai import load_openai_sdk, generate_text_streaming, compute_embedding
from llms.embeddings import load_hf_embedding_model
from cache.redis import get_redis_connection
from services.llm.llm import LLMService
from services.llm.worker import Worker
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


healthcheck = FastAPI()


@healthcheck.get("/")
def index():
    log().debug("healthcheck ok.")
    return {"message": "I'm still alive"}


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
    server = Server(config)
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

    log().info("waiting 60 seconds before terminating worker")
    await asyncio.sleep(60)
    log().info("worker terminated.")


async def _graceful_shutdown(signal, tasks):
    log().info(f"Received exit signal {signal.name}...")
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    asyncio.get_event_loop().stop()


async def _run_worker_main_with_healthcheck():
    task1 = asyncio.create_task(_start_health_check_endpoint())
    task2 = asyncio.create_task(worker_main())
    await asyncio.gather(task1, task2)


async def main():
    tasks = [asyncio.create_task(_start_health_check_endpoint()), asyncio.create_task(worker_main())]
    loop = asyncio.get_running_loop()

    for sig in [signal.SIGINT, signal.SIGTERM]:
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(_graceful_shutdown(s, tasks)))

    await asyncio.gather(*tasks)


def sync_main():
    asyncio.run(main())


if __name__ == "__main__":
    sync_main()
