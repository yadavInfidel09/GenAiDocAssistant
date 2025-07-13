import openai
import os

def generate_summary(text, max_words=150):
    client = openai.OpenAI()
    prompt = f"Summarize the following document in no more than {max_words} words:\n\n{text}"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes documents."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.3
    )
    summary = response.choices[0].message.content.strip()
    return summary
