# to get different motiv or meaningfull quotes in every reloading
import requests, re
from deep_translator import GoogleTranslator




def home_page_quote():
    def extract_quotes(text):
        return re.findall(r'\$%quo%\$(.*?)\$%quo%\$', text)[0]

    user_message = "I need 1 quote that changes all the time for the home page of my dictionary project, you can create it. Motive or meaning. So that I can easily distinguish them from your answer, write the quote inside the following characters: $%quo%$ your quote here $%quo%$, 1 is enough and length must be 35"
    url = "https://gemini-6y6e.onrender.com/api/chat"
    payload = {"message": user_message}  
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
            
        data = response.json()
        return extract_quotes(data.get("response"))

    except:
        return "Unlock the world, one word at a time."
    
# ENG-UZB and UZB-ENG

def translate(text):
    return GoogleTranslator(source='en', target='uz').translate(text)

# get the word from aip
def extract_data(response_text):
    pattern = r"\?\?\?json_code_area_start\?\?\?\s*\{(.*?)\}\s*\?\?\?json_code_area_end\?\?\?"
    match = re.search(pattern, response_text, re.DOTALL)
    
    if not match:
        return "No match found"  # Return an error message if no match is found

    code_block = match.group(1).strip()

    try:
        # Convert the extracted JSON-like text into a Python dictionary
        data = eval("{" + code_block + "}")  # eval should be used carefully; better to use json.loads after fixing the format
    except Exception as e:
        return f"Error in parsing: {e}"

    return {
        "definitions": data.get("definitions", []),
        "synonyms": data.get("synonyms", []),
        "antonyms": data.get("antonyms", []),
        "phonetics": data.get("phonetics", []),
        "examples": data.get("examples", [])
    }

def get_aip_response(user_message):
    url = "https://gemini-6y6e.onrender.com/api/chat"  # Your API endpoint
    payload = {
        "message": f"""
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
        DON'T FORGET TO GIVE AT LEAST 3 EXAMPLES FOR EVERYONE (I SAID MINIMUM, NOT ALWAYS, THE MORE AND THE MORE CLEAR, THE BETTER)
        TTHESE SITUATIONS MAY BE IN THE SUBJECT OF THE WORDS NUDITY GIVEN IN THE BASE, BLANK ANSWERS WILL BE RETURNED
        Given word: {user_message}
        """
    }

    try:
        response = requests.post(url, json=payload, timeout=10)  # Send request
        response.raise_for_status()  # Raise error for bad status codes (4xx, 5xx)
        
        data = response.json()  # Convert response to JSON
        return extract_data(data.get("response", ""))  # Extract AI's response

    except requests.exceptions.RequestException as e:
        return f"Request error: {e}"

