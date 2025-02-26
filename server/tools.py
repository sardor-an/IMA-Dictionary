# to get different motiv or meaningfull quotes in every reloading
import requests, re
from deep_translator import GoogleTranslator

def home_page_quote():
    def extract_quotes(text):
        return re.findall(r'\$\+\$(.*?)\$\+\$', text)[0]

    user_message = "I need 1 quote that changes all the time for the home page of my dictionary project, you can create it. Motive or meaning. So that I can easily distinguish them from your answer, write the quote inside the following characters: $+$ you quote here $+$, 1 is enough and length must be 35"
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

def translate(text, source, target):
    return GoogleTranslator(source=source, target=target).translate(text)

    
