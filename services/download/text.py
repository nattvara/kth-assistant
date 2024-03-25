import unicodedata

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
    text = soup.get_text()
    text = text.strip()
    text = remove_triple_newlines(text)
    text = strip_air(text)
    text = replace_nonsafe_characters_with_spaces(text)
    return text
