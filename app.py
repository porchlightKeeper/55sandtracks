import os
from flask import Flask

import secret

app = Flask(__name__)

OPENAI_KEY = os.environ.get(secret.OPENAI_KEY)

@app.route('/')
def index():
    if OPENAI_KEY:
        return f'API Key found hehe'
    else:
        return 'API Key not found.'

if __name__ == '__main__':
    app.run(debug=True)