# # from deep_translator import GoogleTranslator

# # translator = GoogleTranslator(source="en", target="uz")
# # translated = translator.translate("Hello, how are you?")
# # print(translated)  

# # men senga 1 ta inglizcha so'z beraman sen esa menga uning definitionlarini, sinonimlarini, antonimlarini,phonetic(us va uk) va so'zni tushunish va qo'llay olish uchun real example gaplar berasan.Faqat javobingdan ularni oson ajratib olishim uchun men bergan patterndan foydalan.
# # ?DEF? bu yerda definitionlarni python list ko'rinishida yozasan ?DEF?
# # # Mendan senga namuna ?DEF? ['definition1', 'definition2', 'definition3', ...] ?DEF?

# # ?SYN? bu yerda sinonimlar python list ko'rinishida yozasan ?SYN?
# # # Mendan senga namuna ?SYN? ['sinonim1', 'sinonim2', 'sinonim3', ...]?SYN?

# # ?ANT?bu yerda  antonimlarni python list ko'rinishida yoz?ANT?
# # # Mendan senga namuna ?ANT? ['antonim1', 'antonim2', 'antonim3', ...]?ANT?

# # ?PHO?bu yerda  phonetics python list ko'rinishida yoz ?PHO?
# # # Mendan senga namuna ?PHO? ['phonetic of us', 'phonetic of uk']?PHO?

# # ?EXA? bu yerda example gaplarni yozasan - boshqalarida biroz farqi, aynan shu gapda berilgan so'z qaysi so'z turkumida ekanligini ham yoz. ?EXA?
# # #Mendan senga namuma ?EXA? [('example sentence', 'word class of given word in this sentence')] ?EXA?

# # # Barcha so'rovlar mavjud bo'lishini taminla - har bir so'rovda definitionlar, sinonimlar, antonimlar, phoneticlar va examplelar bo'lishi shart

# # VA UNUTMA QATORLAR ORASIDA BO'SHLIQ QOLDIRMAY YOZ
# # # TUSHUNISHING UCHUN MISOL BERAMAN
# # ?DEF? ['definition1', 'definition2', 'definition3', ...] ?DEF?
# # ?SYN? ['sinonim1', 'sinonim2', 'sinonim3', ...]?SYN?
# # ANT? ['antonim1', 'antonim2', 'antonim3', ...]?ANT?
# # ?PHO? ['phonetic of us', 'phonetic of uk']?PHO?
# # ?EXA? [('example sentence', 'word class of given word in this sentence')] ?EXA?

# # BERILGAN SO'Z 

# import enchant

# dictionary = enchant.Dict("en_US")

# def is_english_word(word):
#     return dictionary.check(word)

# print(is_english_word("return"))  # True
# print(is_english_word("houese"))  # False

import requests



prm = """
        I will give you 1 English word and you will give me its definition, translation of definitions to uzbek, synonyms, antonyms, phonetic (us and uk) and real example sentences to understand and use the word. Just use the pattern I gave so that I can easily extract them from your answer
        You write the part of the answer I need in this pattern:
        ```json
        {{
            "definitions": ["definition1", "definition2", "definition3"],
            "definitions_uz": ["definition_uz1", "definition_uz2", "definition_uz3"],
            "synonyms": ["synonym1", "synonym2", "synonym3"],
            "antonyms": ["antonym1", "antonym2", "antonym3"],
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
        - There should be at least 5 examples in each section (at least 5 definitions, at least 5 synonyms, and so on for all.But only examples must be more than 15 in many different cases)
        - REMEMBER I said at least 5, I didn't always say 5, it's okay if there are more.
        - Take examples from real situations and make sure they are understandable.
        So let's start!
        Given word: beatiful

"""

