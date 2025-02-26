

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from werkzeug.security import check_password_hash, generate_password_hash

from server.db import get_db
from server.tools import get_aip_response, translate

word = Blueprint('word', __name__, url_prefix='/word')

@word.route('/search/<word>')
def search_word(word):

    # word_data = json.loads(get_aip_response(word))

    # phonetics = word_data["phonetics"]
    # definitions = word_data["definitions"]
    # synonyms = word_data["synonyms"]
    # antonyms = word_data["antonyms"]
    # examples = word_data["examples"]
    # return render_template('word_page.html',
    #           phonetics = phonetics,
    #           definitions = definitions,
    #           synonyms = synonyms,
    #           antonyms = antonyms,
    #           examples = examples,
    #           word=word,
    #           translate= translate)

    return get_aip_response(word)