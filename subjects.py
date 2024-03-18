import base64
from typing import List
from flask import url_for

import gpt
import storage
import text_utils


def encode_subject_context(subject_context: str) -> str:
    return base64.urlsafe_b64encode(subject_context.encode('utf-8'))


def decode_subject_context(encoded_context: str) -> str:
    return base64.b64decode(encoded_context).decode('utf-8').strip()


def add_links(text: str, use_context=False) -> str:
    """
    Replace occurrences of subject names in the provided text with hyperlinks to their respective paths.

    :param text: The text in which subject names are to be replaced with hyperlinks.
    :param subjects: A list of subject names.
    :param use_context: Whether to provide additional context about each subject.
    :return: The modified text with subject names replaced with hyperlinks.
    """
    subjects = gpt.find_new_subjects(text)

    # Register these new subjects.
    storage.create_subjects(subjects)

    # Link them in the text!
    for subject in subjects:
        context = None
        if use_context:
            subject_context = gpt.get_context(text, subject)
            context = text_utils.encode_subject_context(subject_context)

        safe_subject = text_utils.text_to_subject(subject)

        url = url_for('new_article', subject=safe_subject, context=context)
        text = text.replace(subject, f"[{subject}]({url})")
    return text
