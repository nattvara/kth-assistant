from os.path import basename
import asyncio
import sys

from services.llm.supported_models import get_enum_from_enum_name
from services.llm.llm import LLMService
from services.llm.worker import Worker
from config.logger import log


def print_help():
    help_message = f"""
Usage: {basename(sys.argv[0])} MISTRAL_7B_INSTRUCT

This program starts a worker for a given model.

Arguments:
    MODEL_NAME    The name of the model to run (e.g., MISTRAL_7B_INSTRUCT).

Example:
    {basename(sys.argv[0])} MISTRAL_7B_INSTRUCT
"""
    print(help_message)


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ['-h', '--help']:
        print_help()
        exit(1)

    enum_name = sys.argv[1]
    try:
        model_enum = get_enum_from_enum_name(enum_name)
    except KeyError:
        print("Invalid model name")
        exit(1)

    log().info("Starting worker")
    service = LLMService(model_enum)
    worker = Worker(service, model_enum, device='mps')
    asyncio.run(worker.run())


if __name__ == '__main__':
    main()
