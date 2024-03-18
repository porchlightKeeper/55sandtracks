import os
from flask import Flask, redirect, url_for
import openai

import gpt
import storage
import secret
import constants
import text_utils

openai.api_key = os.environ.get(secret.OPENAI_KEY)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ[secret.DATABASE_URL].replace(
    "postgres://", "postgresql://")
storage.db.init_app(app)

with app.app_context():
    # Ensure the root subject is created.
    storage.create_subject(constants.ROOT_SUBJECT)


@app.route('/')
def root():
    subject = text_utils.text_to_subject(constants.ROOT_SUBJECT)
    return redirect(url_for('new_article', subject=subject))


@app.route('/<path:subject>/')
def new_article(subject: str):
    subject = text_utils.text_to_subject(subject)
    if storage.is_supported_subject(subject):
        text = gpt.write_article(subject.replace("-", " "))

        # Our new article might link to interesting new subjects!
        new_subjects = gpt.find_new_subjects(text)

        # Register these new subjects.
        storage.create_subjects(new_subjects)

        # Link them in the text!
        text = text_utils.link_subjects_in_text(text, new_subjects)

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
    app.run(debug=True)
