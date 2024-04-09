import unicodedata

import pdfminer.high_level as pmine
from bs4 import BeautifulSoup


def remove_triple_newlines(text):
    if "\n\n\n" not in text:
        return text
    return remove_triple_newlines(text.replace("\n\n\n", "\n\n"))


def strip_air(text):
    stripped_lines = [line.strip() for line in text.split('\n') if line.strip()]
    return '\n'.join(stripped_lines)


def replace_nonsafe_characters_with_spaces(input_str):
    cleaned_str = ""
    for c in unicodedata.normalize('NFKD', input_str):
        if unicodedata.category(c) in ('Cc', 'Cf', 'Zs', 'Zl', 'Zp'):
            cleaned_str += ' '
        else:
            cleaned_str += c
    return cleaned_str


def extract_text_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for a_tag in soup.find_all('a'):
        href = a_tag.get('href', '')
        text = a_tag.text
        formatted_link = f"\document{{{href}}}{{{text}}}"
        a_tag.replace_with(formatted_link)

    text = soup.get_text()
    text = text.strip()
    text = remove_triple_newlines(text)
    text = strip_air(text)
    text = replace_nonsafe_characters_with_spaces(text)
    return text


def extract_text_from_pdf_file(file_path: str) -> str:
    text = pmine.extract_text(file_path)
    text = text.strip()
    text = replace_nonsafe_characters_with_spaces(text)
    return text


def extract_text_from_plaintext_file(file_path: str) -> str:
    with open(file_path, 'r') as f:
        text = f.read()
        text = text.strip()
        text = replace_nonsafe_characters_with_spaces(text)
        return text
