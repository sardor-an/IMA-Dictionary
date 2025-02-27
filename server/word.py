

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug import exceptions

from server.db import get_db
from server.tools import get_aip_response,  check_if_word_exists, string_make_for_list, str_json

word = Blueprint('word', __name__, url_prefix='/word')

@word.route('/search/<word>')
def search_word(word):
        from flask import jsonify
        db = get_db()
        new_word = get_aip_response(word)
    
    # if check_if_word_exists(word):  # Global check if the word exists
        word_check = db.execute('SELECT * FROM Word WHERE word = ?', (word,)).fetchone()  # Local check in our database
        if not word_check:
            # Fetch word data from AI
            
#             # ADDING NEW WORD 
            db.execute('INSERT INTO Word (word, uzbek_translation) VALUES (?, ?)', (word, new_word['uzbek_translation']))

            # get word that has just been added
            new_added_word = db.execute('SELECT * FROM Word WHERE word = ?', (word, )).fetchone()
            

            for defintion in new_word['definitions']:
                db.execute('INSERT INTO Definition (word_id, definition) VALUES (?, ?)', (new_added_word['id'], defintion))
            
            for defintion_uz in new_word['definitions_uz']:
                db.execute('INSERT INTO Definition_uz (word_id, definition) VALUES (?, ?)', (new_added_word['id'], defintion_uz))

            for synonym in new_word['synonyms']:
                db.execute('INSERT INTO Synonym (word_id, synonym) VALUES (?, ?)', (new_added_word['id'], synonym))

            for antonym in new_word['antonyms']:
                db.execute('INSERT INTO Antonym (word_id, antonym) VALUES (?, ?)', (new_added_word['id'], antonym))
            
            for example in new_word['examples']:
                db.execute('INSERT INTO Example (word_id, example, word_class) VALUES (?, ?, ?)', (new_added_word['id'], example['sentence'], example['word_class']))
            
            for phonetic in new_word['phonetics']:
                db.execute('INSERT INTO Phonetics (word_id, phonetic) VALUES (?, ?)', (new_added_word['id'], phonetic))

            for paronym in new_word['paronyms']:
                db.execute('INSERT INTO Example (word_id, paronym) VALUES (?, ?)', (new_added_word['id'], paronym))
            


            db.commit()

        # Retrieve and return word details
        nothing = db.execute('SELECT * FROM Word WHERE word = ?', (word, )).fetchone()
        word_details = {
    'paronyms': [row[0] for row in db.execute('SELECT paronym FROM Paronyms WHERE word_id = ?', (nothing['id'],)).fetchall()],
    'definitions': [row[0] for row in db.execute('SELECT definition FROM Definition WHERE word_id = ?', (nothing['id'],)).fetchall()],
    'synonyms': [row[0] for row in db.execute('SELECT synonym FROM Synonym WHERE word_id = ?', (nothing['id'],)).fetchall()],
    'antonyms': [row[0] for row in db.execute('SELECT antonym FROM Antonym WHERE word_id = ?', (nothing['id'],)).fetchall()],
    'examples': [row[0] for row in db.execute('SELECT example FROM Example WHERE word_id = ?', (nothing['id'],)).fetchall()],
    'phonetics': [row[0] for row in db.execute('SELECT phonetic FROM Phonetics WHERE word_id = ?', (nothing['id'],)).fetchall()],
    'definitions_uz': [row[0] for row in db.execute('SELECT definition FROM Definition_uz WHERE word_id = ?', (nothing['id'],)).fetchall()],
    'uzbek_translation':nothing['uzbek_translation']
}
        print(word_details)
        
        if g.history_wordlist:
            if not db.execute('SELECT * FROM wordlist_word WHERE word_id = ? AND wordlist_id = ?', (nothing['id'], g.history_wordlist['id'])).fetchone():
                db.execute('INSERT INTO wordlist_word (word_id, wordlist_id) VALUES (?, ?)', (nothing['id'], g.history_wordlist['id']))
                db.commit()
        # print(word_details)
        # return {'fuck':word_details}

        from .tools import search_unsplash


        return render_template('word_page.html', word = word, word_details = word_details, image = search_unsplash(word))
        # return new_word
    # else:
    #     return {'code':get_suggests(word)}



@word.route('wordlist/create', methods=['GET', 'POST'])
def create_wordlist():
    if request.method == 'POST':
        title = request.form.get('title')

        # need validation check


        db = get_db()

        if not db.execute('SELECT * FROM Wordlist WHERE owner_id = ? AND title = ?', (session.get("user_id"), title)).fetchone():      
            db.execute( "INSERT INTO Wordlist (title, owner_id) VALUES (?, ?)", (title, session.get('user_id')))

            just_created_wordlist_id = db.execute('SELECT * FROM Wordlist WHERE owner_id = ? AND title = ?', (session.get("user_id"), title)).fetchone()

            db.commit()

            

            return redirect(url_for('word.wordlist_view', id = just_created_wordlist_id['id']))

        else:
            print('Please select another name')
        ######how can be fixed
        
    return render_template('create_wordlist.html')

@word.route('wordlist/view/<int:id>')
def wordlist_view(id):
    db = get_db()
    if db.execute('SELECT * FROM Wordlist WHERE id = ?', (id,)).fetchone()['owner_id'] == session.get('user_id'):

        
        wordlist = db.execute('SELECT * FROM Wordlist WHERE id = ?', (id,)).fetchone()
    
        word_ids = db.execute('SELECT * FROM wordlist_word WHERE wordlist_id = ?', (id, )).fetchall()
        items = []
        for item in word_ids:
            
            test = db.execute('SELECT * FROM Word WHERE id = ? ', (item['word_id'], )).fetchone()

            if test:
                items.append(test)


        if wordlist:
            return render_template('wordlist_view.html', wordlist = wordlist, items = items[::-1])
        else:
            return exceptions.NotFound('MAVJUD EMAS')
    
    else:
        return exceptions.Forbidden("SIZDA BU MANZIL UCHUN RUXSAT YO'Q")



@word.route('/my-wordlists')
def my_wordlists():
    if g.user:
        user_wordlists = get_db().execute('SELECT * FROM Wordlist WHERE owner_id = ?', (session.get('user_id'),))
        return render_template('my_wordlists.html', user_wordlists = user_wordlists)
    return redirect(url_for('auth.login'))

from flask import jsonify

@word.route('/delete/<int:id>')
def delete_wordlist(id):
        db = get_db()
    # if request.method == 'POST':
        check_if_wordlist = db.execute('SELECT * FROM Wordlist WHERE id = ?', (id,)).fetchone()
        
        if check_if_wordlist:
            db.execute('DELETE FROM Wordlist WHERE id = ?', (id,))
            db.commit()
            return redirect(url_for('word.my_wordlists'))
        else:
            return jsonify({"success": False, "message": "Wordlist not found."}), 404
