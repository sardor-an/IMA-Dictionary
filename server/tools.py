import requests
import re
import json
from deep_translator import GoogleTranslator

def home_page_quote():
    def extract_quotes(text):
        match = re.search(r'\$%quo%\$(.*?)\$%quo%\$', text, re.DOTALL)
        return match.group(1).strip() if match else "Unlock the world, one word at a time."

    user_message = "I need 1 quote that changes all the time for the home page of my dictionary project, you can create it. Motive or meaning. So that I can easily distinguish them from your answer, write the quote inside the following characters: $%quo%$ your quote here $%quo%$, 1 is enough and length must be 35"
    url = "https://gemini-6y6e.onrender.com/api/chat"
    payload = {"message": user_message}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return extract_quotes(data.get("response", ""))
    except requests.RequestException as e:
        print(f"Error fetching quote: {e}")
        return "Unlock the world, one word at a time."

# ENG-UZB and UZB-ENG translation
def translate(text):
    return GoogleTranslator(source='en', target='uz').translate(text)

# Extract data from API response
def extract_data(response_text):
    pattern = r"\?\?\?json_code_area_start\?\?\?\s*(\{.*?\})\s*\?\?\?json_code_area_end\?\?\?"
    match = re.search(pattern, response_text, re.DOTALL)

    if not match:
        return {"error": "No valid JSON data found in response"}

    json_block = match.group(1).strip()

    try:
        data = json.loads(json_block)  # Securely parse JSON
        return {
            "definitions": data.get("definitions", []),
            "synonyms": data.get("synonyms", []),
            "antonyms": data.get("antonyms", []),
            "phonetics": data.get("phonetics", []),
            "examples": data.get("examples", [])
        }
    except json.JSONDecodeError as e:
        return {"error": f"JSON parsing failed: {e}"}

def get_aip_response(user_message):
    url = "https://gemini-6y6e.onrender.com/api/chat"
    payload = {"message": f"""
        I will give you 1 English word and you will give me its definition, synonyms, antonyms, phonetic (us and uk) and real example sentences to understand and use the word. Just use the pattern I gave so that I can easily extract them from your answer
        You write the part of the answer I need in this pattern:
        ???json_code_area_start???
        {{
            "definitions": ["definition1", "definition2", "definition3"],
            "synonyms": ["synonym1", "synonym2", "synonym3"],
            "antonyms": ["antonym1", "antonym2", "antonym3"],
            "phonetics": ["phonetic of US", "phonetic of UK"],
            "examples": [
                {{"sentence": "Example sentence 1", "word_class": "noun"}},
                {{"sentence": "Example sentence 2", "word_class": "verb"}}
            ]
        }}
        ???json_code_area_end???
        Let me explain more about what to write in Examples: in English, 1 word can have several meanings and come in different word classes. In one place as a noun, in another as a verb, etc. Here, the first element of the tuple is the adjective clause, and as the second element, write which word class the given word comes in.
        # Guideline
        - There should be at least 5 examples in each section (at least 5 definitions, at least 5 synonyms, and so on for all.But only examples must be more than 15 in many different cases)
        - REMEMBER I said at least 5, I didn't always say 5, it's okay if there are more.
        - Take examples from real situations and make sure they are understandable.
        So let's start!
        Given word: {user_message}
    """}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return extract_data(data.get("response"))
        # return data.get("response")
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {e}"}
