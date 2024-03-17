import os
from flask import Flask
import openai

from gpt import gpt3
import secret

app = Flask(__name__)

openai.api_key = os.environ.get(secret.OPENAI_KEY)

@app.route('/')
def index():
    return gpt3("There once was a ")

if __name__ == '__main__':
    app.run(debug=True)