import os
from flask import Flask, redirect, url_for
import openai


import gpt
from storage import DatabaseManager
import secret
import constants
import text_utils

openai.api_key = os.environ.get(secret.OPENAI_KEY)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ[secret.DATABASE_URL]
db = DatabaseManager(app)
db.create_subject(constants.ROOT_SUBJECT)


@app.route('/', defaults={'subject': None, 'number': None})
def root():
    return redirect(url_for('index', subject=constants.ROOT_SUBJECT))


@app.route('/<path:subject>/', defaults={'number': None})
def new_article(subject: str):
    if db.is_supported_subject(subject):
        text = gpt.write_article(subject.replace("-", " "))

        # Our new article might link to interesting new subjects!
        new_subjects = gpt.find_new_subjects(text)

        # Register these new subjects.
        db.create_subjects(new_subjects)

        # Link them in the text!
        text = text_utils.link_subjects_in_text(text, new_subjects)

        # Save this text to a new page.
        number = db.save_content(subject, text)
        return redirect(url_for('index', subject=subject, number=number))
    else:
        return text_utils.render_markdown(constants.UNSUPPORTED_SUBJECT_TEXT)


@app.route('/<path:subject>/<int:number>')
def index(subject, number):
    text = db.load_content(subject, number)
    if text is None:
        text = constants.UNSUPPORTED_NUMBER_TEXT
    return text_utils.render_markdown(text)


if __name__ == '__main__':
    app.run(debug=True)
