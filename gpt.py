import ast
from typing import List
import nltk
import openai

import text_utils
import storage

ENGINE = "gpt-3.5-turbo-instruct"
MAX_NEW_TOKENS = 2048


# PROMPT STRINGS
SUBJECT = "{{SUBJECT}}"
ARTICLE = "{{ARTICLE}}"


def _load_prompt(filepath: str) -> str:
    prompt = ""
    with open(filepath, 'r') as f:
        prompt = f.read()
    if not prompt:
        raise Exception("could not read prompt at {filepath}")
    return prompt


def _gpt3(prompt: str, temperature=0.66) -> str:
    max_tokens = int(
        min(MAX_NEW_TOKENS, 4096-1.2*len(nltk.word_tokenize(prompt)))
    )

    if max_tokens < 10:
        raise Exception("prompt was too long, lol.")

    engine = "gpt-3.5-turbo-instruct"
    frequency_penalty = 2.0
    presence_penalty = 2.0

    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        n=1,
        max_tokens=max_tokens,
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        # stop="##"
    )
    text = response.choices[0].text.strip()

    text_preview = text[:25] if len(text) >= 25 else text
    print(f"text: {text_preview}...")

    return text


def find_new_subjects(text: str) -> List[str]:
    prompt = _load_prompt("./prompts/find_new_subjects.txt")
    prompt = prompt.replace(ARTICLE, text)
    response = _gpt3(prompt, temperature=0.0)
    subject_list = []
    # Expect to parse the response as a list!
    try:
        response = response.replace("\n", "").strip()
        subject_list = ast.literal_eval(response)
        subject_list = [subject for subject in subject_list if len(
            subject_list) < storage.SUBJECT_CHAR_LIMIT]
    except:
        print(f'Could not parse {response}')
    return subject_list


def write_article(subject: str) -> str:
    subject = text_utils.subject_to_text(subject)
    prompt = _load_prompt("./prompts/article.txt")
    prompt = prompt.replace(SUBJECT, subject)
    return _gpt3(prompt)
