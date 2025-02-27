import requests
import re
import json
from deep_translator import GoogleTranslator
from .db import get_db
import ast

def home_page_quote():
    def extract_quotes(text):
        match = re.search(r'\$%quo%\$(.*?)\$%quo%\$', text, re.DOTALL)
        return match.group(1).strip() if match else "Unlock the world, one word at a time."

    user_message = "I need 1 quote that changes all the time for the home page of my dictionary project, you can create it. Motive or meaning. So that I can easily distinguish them from your answer, write the quote inside the following characters: $%quo%$ your quote here $%quo%$, 1 is enough and length must be 35"
   

    res = get_gemini_response(user_message)

    try:
        return extract_quotes(res)
    except requests.RequestException as e:
        print(f"Error fetching quote: {e}")
        return "Unlock the world, one word at a time."

# ENG-UZB and UZB-ENG translation
def translate(text):
    return GoogleTranslator(source='en', target='uz').translate(text)

# Extract data from API response
def extract_data(response_text):
    pattern = r"```json\s*({.*?})\s*```"# THERE SHOULD BE OTHER PATTERNS TO BE CONFIDENT
    match = re.search(pattern, response_text, re.DOTALL)

    if not match:
        return {"error": "No valid JSON data found in response"}

    json_block = match.group(1).strip()

    try:
        data = json.loads(json_block)  # Securely parse JSON
        return {
            "uzbek_translation":data.get('uzbek_translation', []),
            "definitions": data.get("definitions", []),
            "definitions_uz":data.get('definitions_uz', []),
            "synonyms": data.get("synonyms", []),
            "antonyms": data.get("antonyms", []),
            'paronyms': data['paronyms'],
            "phonetics": data.get("phonetics", []),
            "examples": data.get("examples", [])
        }
    except json.JSONDecodeError as e:
        return {"error": f"JSON parsing failed: {e}"}

def get_aip_response(user_message):
    prm = f"""
        I will give you 1 English word and you will give me its translation of this word in uzbek,definition, translation of definitions to uzbek, synonyms, antonyms,paronyms, phonetic (us and uk) and real example sentences to understand and use the word. Just use the pattern I gave so that I can easily extract them from your answer
        You write the part of the answer I need in this pattern:
        ```json
        {{
            "uzbek_translation:'uzbek translations here',
            "definitions": ["definition1", "definition2", "definition3"],
            "definitions_uz": ["definition_uz1", "definition_uz2", "definition_uz3"],
            "synonyms": ["synonym1", "synonym2", "synonym3"],
            "antonyms": ["antonym1", "antonym2", "antonym3"],
            "paronyms": ["paronym1", "paronym2", "paronym3"],
            "phonetics": ["phonetic of US", "phonetic of UK"],
            "examples": [
                {{"sentence": "Example sentence 1", "word_class": "noun"}},
                {{"sentence": "Example sentence 2", "word_class": "verb"}}
            ]
        }}
        ```
               
        Let me explain more about what to write in Examples: in English, 1 word can have several meanings and come in different word classes. In one place as a noun, in another as a verb, etc. Here, the first element of the tuple is the adjective clause, and as the second element, write which word class the given word comes in.
        # Guideline
        - Do not forget about adding uzbek translations of definitions
        - Your response must look exactly like this JSON structure. Do NOT add extra fields or remove any
        - No extra explanations. Only output the JSON structure.
        - You MUST strictly follow the JSON pattern below. Do NOT modify the structure, order, or format of the response.
        - There should be at least 5 examples in each section (at least 5 definitions, at least 5 synonyms, and so on for all.But only examples always must be 20  in many different cases)
        - REMEMBER I said at least 5, I didn't always say 5, it's okay if there are more.And their max is 10;
        - Take examples from real situations and make sure they are understandable.
        So let's start!
        Given word: {user_message}
    """

    return extract_data(get_gemini_response(prm))


def string_make_for_sql(data: list, uz = False):
    data_for_sql = ""
    if uz:
        for item in data:
            data_for_sql += f'{translate(item)}'

    else:
        for item in data:
            data_for_sql += f'{item};'

    return data_for_sql

def string_make_for_list(data: str):
    return data.split(';')[:-1]

def str_json(data):
    return ast.literal_eval(f"[{re.findall(r"\{'sentence': '([^']+)', 'word_class': '([^']+)'\}", data)[0]}]")


def check_if_word_exists(word):
    db = get_db().execute("SELECT EXISTS(SELECT 1 FROM Saved_word WHERE word = ?)", (word,)).fetchone()[0]
    return bool(db)

# def get_suggests(word):
#     # from rapidfuzz import process
#     def suggest_similar(word, num_suggestions=5):
#         db = get_db()
#         cursor = db.execute("SELECT word FROM Saved_Word")
#         all_words = [row[0] for row in cursor.fetchall()]
#         matches = process.extract(word, all_words, limit=num_suggestions, score_cutoff=80)
#         return [match[0] for match in matches] or "Nothing"

#     return suggest_similar(word, 10)
API_KEY = "AIzaSyBEAU0Np4eVQwyy_HV08gerXQ7slfKKKzw"
def get_gemini_response(prm,api_key = API_KEY):
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prm}]
        }]
    }

    response = requests.post(url, json=data, headers=headers).json()

    # Extract only the response text
    try:
        return response["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return "No valid response"

import requests

def search_unsplash(text, per_page=10):
    key = 'nKnKTDLfF-u8ty8Dvdqqkpg1TIYjQBxp91oG08Cel_k'
    url = f"https://api.unsplash.com/search/photos?page=1&query={text}&client_id={key}&per_page={per_page}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return [(photo['urls']['regular'], photo.get('alt_description', 'No description available')) for photo in data['results']]
    else:
        return f"Error: {response.status_code}, {response.json()}"

def get_the_word(word_id):
    return get_db().execute('SELECT * FROM Word WHERE id = ?', (word_id, )).fetchone()
def get_definitions(word_id):
    return get_db().execute('SELECT * FROM Definition WHERE word_id = ?', (word_id, )).fetchall()

def get_definitions_uz(word_id):
    return get_db().execute('SELECT * FROM Definition_uz WHERE word_id = ?', (word_id, )).fetchall()

def get_synonyms(word_id):
    return get_db().execute('SELECT * FROM Synonym WHERE word_id = ?', (word_id, )).fetchall()


def get_antonyms(word_id):
    return get_db().execute('SELECT * FROM Antonym WHERE word_id = ?', (word_id, )).fetchall()

def get_paronyms(word_id):
    return get_db().execute('SELECT * FROM Paronyms WHERE word_id = ?', (word_id, )).fetchall()

def get_examples(word_id):
    return get_db().execute('SELECT * FROM Example WHERE word_id = ?', (word_id, )).fetchall()

def get_phonetics(word_id):
    return get_db().execute('SELECT * FROM Phonetics WHERE word_id = ?', (word_id, )).fetchall()


import re
def extract_data_1(text):
    pattern = r"```html\s*(.*?)\s*```"

    match = re.search(pattern, text, re.DOTALL)  # Search for the pattern
    if match:
        return match.group(1).strip()  # Return extracted data without extra spaces
    return None  # Return None if no match is found

def get_audio_url(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"

    try:
        response = requests.get(url)
        data = response.json()

        if isinstance(data, list) and "phonetics" in data[0]:
            for phonetic in data[0]["phonetics"]:
                if "audio" in phonetic and phonetic["audio"]:
                    return phonetic["audio"]

        return "No pronunciation audio found."

    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"