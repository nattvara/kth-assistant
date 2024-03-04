import time

from db.models import PromptHandle
from services.llm import LLMService
from config.logger import log


class Worker:

    def __init__(self, service: LLMService):
        self.service = service
        self.running = False

    def process_handle(self, handle):
        log().info(f"Processing handle with id {handle.id} created at {handle.created_at}")
        log().debug(f"The prompt of the handle is: \"{handle.prompt}\"")

        handle.state = PromptHandle.States.FINISHED
        handle.save()

    def run(self):
        self.running = True
        while self.running:
            try:
                if self.service.has_next():
                    handle = self.service.checkout()
                    self.process_handle(handle)
                time.sleep(0.05)
            except KeyboardInterrupt:
                log().info("Stopping worker...")
                self.stop()

    def stop(self):
        self.running = False


if __name__ == '__main__':
    log().info('Starting worker')
    worker = Worker(service=LLMService())
    worker.run()
