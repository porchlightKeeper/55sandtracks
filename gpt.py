import nltk
import openai

ENGINE = "gpt-3.5-turbo-instruct"
MAX_NEW_TOKENS = 2048

def gpt3(prompt: str) -> str:
    max_tokens = int(
        min(MAX_NEW_TOKENS, 4096-1.2*len(nltk.word_tokenize(prompt)))
    )

    if max_tokens < 10:
        raise Exception("prompt was too long, lol.")

    engine = "gpt-3.5-turbo-instruct"
    temperature = 1.0
    frequency_penalty = 2.0
    presence_penalty = 2.0

    response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        n=1,
        max_tokens=max_tokens,
        temperature=temperature,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        # stop="##"
    )
    text = response.choices[0].text.strip()

    text_preview = text[:25] if len(text) >= 25 else text
    print(f"temperature: {temperature}\ntext: {text_preview}...")

    return text
