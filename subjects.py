import base64
from flask import url_for

import gpt
import storage
import text_utils


def encode_subject_context(subject_context: str) -> str:
    return base64.urlsafe_b64encode(subject_context.encode('utf-8'))


def decode_subject_context(encoded_context: str) -> str:
    return base64.b64decode(encoded_context).decode('utf-8').strip()


def add_links(text: str, current_subject: str, use_context=False) -> str:
    """
    Replace occurrences of subject names in the provided text with hyperlinks to their respective paths.

    :param text: The text in which subject names are to be replaced with hyperlinks.
    :param existing_subject: The current subject of the text, so it is not linked again.
    :param use_context: Whether to provide additional context about each subject.
    :return: The modified text with subject names replaced with hyperlinks.
    """
    subjects = gpt.find_new_subjects(text)

    # Remove the current subject, so the article doesn't link to itself.
    subjects = [subject for subject in subjects if text_utils.text_to_subject(
        subject) != text_utils.text_to_subject(current_subject)]

    # Register these new subjects.
    storage.create_subjects(subjects)

    # First, get the context for each subject.
    contexts = dict()
    if use_context:
        for subject in subjects:
            # subject_context = gpt.get_context(text, subject) # times out
            subject_context = text_utils.get_context(text, subject)
            context = encode_subject_context(subject_context)
            contexts[subject] = context

    # Make a link for each subject!
    for subject in subjects:
        # If we got the context, use it.
        context = contexts[subject] if subject in contexts else None

        safe_subject = text_utils.text_to_subject(subject)
        url = url_for('new_article', subject=safe_subject, context=context)
        link = f"[{subject}]({url})"

        # Replace it carefully, to avoid race conditions.
        text = text.replace(f" {subject} ", "spaces-before-and-after")
        text = text.replace(f" {subject}", "space-before-only")
        text = text.replace(f"{subject} ", "space-after-only")
        text = text.replace("spaces-before-and-after", f" {link} ")
        text = text.replace("space-before-only", f" {link}")
        text = text.replace("space-after-only", f"{link} ")
    return text
