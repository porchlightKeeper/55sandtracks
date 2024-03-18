import random
import re
from typing import List, Union
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from flask_migrate import Migrate

import text_utils


SUBJECT_CHAR_LIMIT = 66
MAX_NUMBER = 666666666


db = SQLAlchemy()


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(
        SUBJECT_CHAR_LIMIT), unique=True)


class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(
        db.Integer, db.ForeignKey('subject.id'), nullable=False)
    number = db.Column(db.Integer)
    text_content = db.Column(db.Text)

    __table_args__ = (
        db.UniqueConstraint(
            'subject_id', 'number', name='unique_subject_number'),
    )


def _get_subject_id(subject: str) -> Union[int, None]:
    subject = Subject.query.filter_by(name=subject).first()
    return subject.id if subject else None


def is_supported_subject(subject: str) -> bool:
    """
    Checks if the given subject name is supported in the database.

    :param subject: The name of the subject to check.
    :return: True if the subject is supported, False otherwise.
    """
    return _get_subject_id(subject) is not None


def create_subjects(subjects: List[str]) -> None:
    """
    Creates new subjects in the database.

    :param subjects: The list of subjects to create.
    """
    for subject in subjects:
        create_subject(subject)


def create_subject(subject: str) -> None:
    """
    Creates a new subject in the database.

    :param subject: The name of the subject to create.
    """
    subject = text_utils.text_to_subject(subject)
    if len(subject) < SUBJECT_CHAR_LIMIT and not is_supported_subject(subject):
        new_subject = Subject(name=subject)
        db.session.add(new_subject)
        db.session.commit()


def load_content(subject: str, number: int) -> Union[str, None]:
    """
    Loads content for the given subject and number.

    :param subject: The subject of the content.
    :param number: The number associated with the content.
    :return: The text content if found, None otherwise.
    """
    subject = text_utils.text_to_subject(subject)
    subject_id = _get_subject_id(subject)
    if subject_id is None:
        raise ValueError(f"Subject {subject} has not been created")

    content = Content.query.filter_by(
        subject_id=subject_id, number=number).first()
    return content.text_content if content else None


def save_content(subject: str, text_content: str) -> int:
    """
    Saves the provided text content associated with the given subject to the database.

    Generates a unique number for the content and creates a new Content instance
    with the provided subject, generated number, and text content. The new instance
    is then added to the database session and committed.

    :param subject: The subject associated with the content.
    :param text_content: The text content to be saved.
    :return: The unique number assigned to the saved content.
    """
    subject = text_utils.text_to_subject(subject)
    subject_id = _get_subject_id(subject)
    if subject_id is None:
        raise ValueError(f"Subject {subject} has not been created")

    new_number = _new_number(subject_id)
    new_content = Content(
        subject_id=subject_id, number=new_number, text_content=text_content)
    db.session.add(new_content)
    db.session.commit()

    return new_number


def _new_number(subject_id: int, max_tries=66) -> int:
    """
    Generate a new random number for the given subject, ensuring uniqueness.

    :param subject_id: The subject_id for which the random number is generated.
    :param max_tries: The maximum number of attempts to generate a unique random number.
    :return: A new unique random number.
    """
    for _ in range(max_tries):
        new_number = random.randint(1, MAX_NUMBER)
        existing_content = Content.query.filter_by(
            subject_id=subject_id, number=new_number).first()
        if not existing_content:
            return new_number
    raise ValueError(
        "Unable to generate a unique random number within the maximum number of tries.")
