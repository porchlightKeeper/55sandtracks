import random
import re
from typing import List, Union
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint


SUBJECT_CHAR_LIMIT = 66
MAX_NUMBER = 666666666


def text_to_subject(text: str) -> str:
    """
    Changes spaces into hyphens, and converts to lowercase.

    Also removes other unsafe chars.

    :param text: The input text to be converted.
    :return: A safe string.
    """
    text = text.strip()
    text = text.replace(' ', '-')
    text = re.sub(r'[^a-zA-Z0-9-_]', '', text)
    return text.lower()  # Convert to lowercase for consistency


def subject_to_text(subject: str) -> str:
    """
    Converts a subject string with hyphens to a text representation.

    :param subject: The subject string with hyphens.
    :return: The text representation of the subject with hyphens replaced by spaces.
    """
    return subject.replace('-', ' ')


class DatabaseManager:
    def __init__(self, app: Flask):
        self.db = SQLAlchemy(app)

        class Subject(self.db.Model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            name = self.db.Column(self.db.String(
                SUBJECT_CHAR_LIMIT), unique=True)

        self.Subject = Subject

        class Content(self.db.Model):
            id = self.db.Column(self.db.Integer, primary_key=True)
            subject_id = self.db.Column(
                self.db.Integer, self.db.ForeignKey('subject.id'), nullable=False)
            number = self.db.Column(self.db.Integer)
            text_content = self.db.Column(self.db.Text)

            __table_args__ = (
                self.db.UniqueConstraint(
                    'subject_id', 'number', name='unique_subject_number'),
            )

        self.Content = Content

    def is_supported_subject(self, subject: str) -> bool:
        """
        Checks if the given subject name is supported in the database.

        :param subject: The name of the subject to check.
        :return: True if the subject is supported, False otherwise.
        """
        subject = text_to_subject(subject)
        subject = self.Subject.query.filter_by(name=subject).first()
        return subject is not None

    def create_subjects(self, subjects: List[str]) -> None:
        """
        Creates new subjects in the database.

        :param subjects: The list of subjects to create.
        """
        for subject in subjects:
            self.create_subject(subject)

    def create_subject(self, subject: str) -> None:
        """
        Creates a new subject in the database.

        :param subject: The name of the subject to create.
        """
        subject = text_to_subject(subject)
        if not self.is_supported_subject(subject):
            new_subject = self.Subject(name=subject)
            self.db.session.add(new_subject)
            self.db.session.commit()

    def load_content(self, subject: str, number: int) -> Union[str, None]:
        """
        Loads content for the given subject and number.

        :param subject: The subject of the content.
        :param number: The number associated with the content.
        :return: The text content if found, None otherwise.
        """
        subject = text_to_subject(subject)
        content = self.Content.query.filter_by(
            subject=subject, number=number).first()
        return content.text_content if content else None

    def save_content(self, subject: str, text_content: str) -> int:
        """
        Saves the provided text content associated with the given subject to the database.

        Generates a unique number for the content and creates a new Content instance
        with the provided subject, generated number, and text content. The new instance
        is then added to the database session and committed.

        :param subject: The subject associated with the content.
        :param text_content: The text content to be saved.
        :return: The unique number assigned to the saved content.
        """
        subject = text_to_subject(subject)
        new_number = self._new_number(subject)
        new_content = self.Content(
            subject=subject, number=new_number, text_content=text_content)
        self.db.session.add(new_content)
        self.db.session.commit()

        return new_number

    def _new_number(self, subject: str, max_tries=66) -> int:
        """
        Generate a new random number for the given subject, ensuring uniqueness.

        :param subject: The subject for which the random number is generated.
        :param max_tries: The maximum number of attempts to generate a unique random number.
        :return: A new unique random number.
        """
        for _ in range(max_tries):
            new_number = random.randint(1, MAX_NUMBER)
            existing_content = self.Content.query.filter_by(
                subject=subject, random_number=new_number).first()
            if not existing_content:
                return new_number
        raise ValueError(
            "Unable to generate a unique random number within the maximum number of tries.")
