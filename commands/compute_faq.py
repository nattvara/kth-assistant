from os.path import basename
from typing import List
import asyncio
import sys

import inquirer

from services.llm.prompts import prompt_common_questions, prompt_deduplicate_questions
from db.actions.course import find_course_by_canvas_id
from services.chat.chat_service import ChatService
from services.llm.supported_models import LLMModel
from db.models import Chat, Message, Course, Faq
from services.llm.llm import LLMService
from config.logger import log


def print_help():
    help_message = f"""
Usage: {basename(sys.argv[0])} CANVAS_ID

This program computes to FAQ for a course.

Arguments:
    CANVAS_ID    The name of the course to compute the FAQ for e.g. 41428

Example:
    {basename(sys.argv[0])} 41428
"""
    print(help_message)


async def extract_questions(chats: List[Chat], course: Course) -> List[str]:
    questions = []
    aggregated_chats = ""
    aggregated_chats_limit = 7500
    questions_limit = 50
    counter = 1
    for chat in chats:
        new_aggregated_chats = add_chat_to_aggregated_chats(aggregated_chats, counter, chat)
        counter += 1

        if len(new_aggregated_chats) > aggregated_chats_limit:
            log().info(f"new_aggregated_chats exceeded {aggregated_chats_limit}")
            questions = questions + await compute_common_questions(aggregated_chats, course)
            aggregated_chats = add_chat_to_aggregated_chats('', counter, chat)
        else:
            aggregated_chats = new_aggregated_chats

        if len(questions) > questions_limit:
            questions = await deduplicate_questions(questions)

    questions = questions + await compute_common_questions(aggregated_chats, course)
    questions = await deduplicate_questions(questions)
    log().info(f"done. computed {len(questions)} common questions")
    return questions


def chat_to_string(chat: Chat) -> str:
    out = ""
    for message in chat.messages:
        out += message_to_string(message) + "\n"
    return out


def message_to_string(message: Message) -> str:
    if message.sender == Message.Sender.STUDENT:
        sender = 'user'
        content = message.content
    else:
        sender = 'assistant'
        if message.prompt_handle is None:
            content = ''
        else:
            content = message.prompt_handle.response
    return f"<|{sender}|> {content}"


def add_chat_to_aggregated_chats(aggregated_chats: str, counter: int, chat: Chat) -> str:
    new = aggregated_chats + f"""
Chat {counter}
{chat_to_string(chat)}


=============================================================================
"""
    return new


async def compute_common_questions(aggregated_chats: str, course: Course) -> List[str]:
    log().debug(f"length of aggregated chats: {len(aggregated_chats)}")

    prompt = prompt_common_questions(aggregated_chats, course.language, course.name)
    log().debug("dispatching prompt_common_questions")
    handle = LLMService.dispatch_prompt(prompt, LLMModel.OPENAI_GPT4)
    handle = await LLMService.wait_for_handle(handle)
    log().debug("received response from openai")

    questions = extract_questions_from_llm_response(handle.response)
    log().debug(f"extracted {len(questions)} questions")
    return questions


async def deduplicate_questions(questions: List[str]) -> List[str]:
    log().debug("deduplicating questions")

    prompt = prompt_deduplicate_questions(questions)
    log().debug("dispatching prompt_deduplicate_questions")
    handle = LLMService.dispatch_prompt(prompt, LLMModel.OPENAI_GPT4)
    handle = await LLMService.wait_for_handle(handle)
    log().debug("received response from openai")

    new_questions = extract_questions_from_llm_response(handle.response)
    log().info(f"deduplicated {len(questions)} questions to {len(new_questions)}")
    return new_questions


def extract_questions_from_llm_response(response: str) -> List[str]:
    split_questions = response.split("<question>")
    extracted_questions = []
    for question in split_questions:
        if "</question>" in question:
            clean_question = question.split("</question>")[0].strip()
            extracted_questions.append(clean_question)
    return extracted_questions


async def main():
    if len(sys.argv) != 2 or sys.argv[1] in ['-h', '--help']:
        print_help()
        exit(1)

    course_id = sys.argv[1]
    log().info(f"computing the faq for course: {course_id}")

    course = find_course_by_canvas_id(course_id)
    if course is None:
        log().info(f"found no course with id: {course_id}")
        exit(1)

    chats = ChatService.find_chats_with_messages_in_course(course)
    log().info(f"found {len(chats)} chats in \"{course.name}\"")

    questions = await extract_questions(chats, course)
    inquirer_questions = [
        inquirer.Checkbox('questions', message="Select the new faq (at least 2)", choices=questions),
    ]
    selected_questions = inquirer.prompt(inquirer_questions)['questions']

    faq_snapshot = ChatService.create_faq_snapshot(course)
    for question in selected_questions:
        faq = Faq(question=question, snapshot=faq_snapshot)
        faq.save()
        log().info("saved new faq.")


def sync_main():
    asyncio.run(main())


if __name__ == '__main__':
    sync_main()
