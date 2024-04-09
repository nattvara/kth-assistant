import asyncio

from playwright.async_api import Page

from services.llm.prompts import prompt_extract_kattis_instruction_from_html
from services.llm.supported_models import LLMModel
from services.llm import llm
from db.models import Url


async def is_instructions(url: Url, page: Page) -> bool:
    await page.goto(url.href)
    await page.wait_for_load_state('load')
    await asyncio.sleep(2)

    container = await page.query_selector('#instructions-container')

    return container is not None


async def get_instruction_text(url: Url, page: Page):
    await page.goto(url.href)
    await page.wait_for_load_state('load')
    await asyncio.sleep(2)

    title = await page.title()

    container = await page.query_selector('#instructions-container')
    content_html = await container.inner_html()

    prompt = prompt_extract_kattis_instruction_from_html(content_html)
    handle = llm.LLMService.dispatch_prompt(prompt, LLMModel.OPENAI_GPT4)
    handle = await llm.LLMService.wait_for_handle(handle)

    return handle.response, title
