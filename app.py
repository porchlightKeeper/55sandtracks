import os
from flask import Flask, redirect, url_for
import openai

import constants
import gpt
import secret
import storage
import subjects
import text_utils


# Flag to determine where to pass along the context when generating the next article.
USE_CONTEXT = True
ROOT_TEXT = text_utils.load_root() if USE_CONTEXT else ""

openai.api_key = os.environ.get(secret.OPENAI_KEY)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ[secret.DATABASE_URL].replace(
    "postgres://", "postgresql://")
storage.db.init_app(app)


@app.route('/')
def root():
    subject = text_utils.text_to_subject(constants.ROOT_SUBJECT)
    if USE_CONTEXT:
        # text = ROOT_TEXT + gpt.complete_root()
        text = gpt.generate_root()

        # Add links for new articles.
        text = subjects.add_links(text, USE_CONTEXT)

        # Save this text to a new page.
        number = storage.save_content(subject, text)
        return redirect(url_for('index', subject=subject, number=number))
    else:
        return redirect(url_for('new_article', subject=subject))


@app.route('/<path:subject>/', defaults={'context': None})
@app.route('/<path:subject>/<string:context>/')
def new_article(subject: str, context: str):
    """
    Display a new article page for the specified subject, optionally with additional context.

    Parameters:
        subject (str): The subject of the article.
        context (str, optional): Base64 encoded string containing context for the subject.

    Returns:
        str: HTML content for the new article page.
    """
    subject = text_utils.text_to_subject(subject)
    if storage.is_supported_subject(subject):
        # Decode the subject context, if given.
        subject_context = subjects.decode_subject_context(
            context) if context else "N/A"

        # Write the article.
        text = gpt.write_article_with_context(
            subject, subject_context) if USE_CONTEXT else gpt.write_article(subject)

        # Add links for new articles.
        text = subjects.add_links(text, subject, USE_CONTEXT)

        # Save this text to a new page.
        number = storage.save_content(subject, text)
        return redirect(url_for('index', subject=subject, number=number))
    else:
        return text_utils.render_markdown(constants.UNSUPPORTED_SUBJECT_TEXT)


@app.route('/<path:subject>/<int:number>')
def index(subject, number):
    subject = text_utils.text_to_subject(subject)
    text = storage.load_content(subject, number)
    if text is None:
        text = constants.UNSUPPORTED_NUMBER_TEXT
    return text_utils.render_markdown(text)


if __name__ == '__main__':
    # Ensure the root subject is created.
    storage.create_subject(constants.ROOT_SUBJECT)

    app.run(debug=True)
