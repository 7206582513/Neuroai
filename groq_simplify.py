import requests

GROQ_API_KEY = ""
GROQ_MODEL = "llama3-8b-8192"

def simplify(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Simplify any given content for a 6th-grade level student in simple words."},
            {"role": "user", "content": text}
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content'].strip()
