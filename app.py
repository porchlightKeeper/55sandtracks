import os
from flask import Flask
import openai
from flaskext.markdown import Markdown

from gpt import gpt3
import secret

openai.api_key = os.environ.get(secret.OPENAI_KEY)

app = Flask(__name__)
Markdown(app)


@app.route('/')
def index():
    return "# 55sandtracks \n ## porchlight keeper \n\n *yes yes yes* \n \n" + gpt3("There once was a ")


if __name__ == '__main__':
    app.run(debug=True)
