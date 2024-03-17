import os
from flask import Flask, render_template_string
import openai
import markdown


from gpt import gpt3
import secret

openai.api_key = os.environ.get(secret.OPENAI_KEY)

app = Flask(__name__)


@app.route('/')
def index():
    text = "# 55sandtracks\n\n## porchlight keeper\n\n*yes yes yes*\n\n"

    text += gpt3("Here are examples of markdown text: ")

    html_content = markdown.markdown(text)
    return render_template_string('{{ content|safe }}', content=html_content)


if __name__ == '__main__':
    app.run(debug=True)
