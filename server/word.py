from flask import Blueprint, g, redirect, render_template, request, session, url_for,render_template, make_response
from werkzeug import exceptions
from server.db import get_db
from server.tools import get_aip_response,  search_unsplash, get_gemini_response, get_audio_url, get_examples
from weasyprint import HTML
from flask import jsonify

word = Blueprint('word', __name__, url_prefix='/word')

@word.route('/search/<word>')
def search_word(word):
    db = get_db()
    word_check = db.execute('SELECT * FROM Word WHERE word = ?', (word,)).fetchone()
    if not word_check:
        new_word = get_aip_response(word)
        if not new_word:  
            return jsonify({'error': 'Word not found in API'}), 404
        db.execute('INSERT INTO Word (word, uzbek_translation) VALUES (?, ?)', 
                   (word, new_word['uzbek_translation']))
        new_word_id = db.execute('SELECT id FROM Word WHERE word = ?', (word,)).fetchone()['id']
        def bulk_insert(table, column, values):
            if values:
                db.executemany(f'INSERT INTO {table} (word_id, {column}) VALUES (?, ?)', 
                               [(new_word_id, v) for v in values])
        bulk_insert('Definition', 'definition', new_word['definitions'])
        bulk_insert('Definition_uz', 'definition', new_word['definitions_uz'])
        bulk_insert('Synonym', 'synonym', new_word['synonyms'])
        bulk_insert('Antonym', 'antonym', new_word['antonyms'])
        bulk_insert('Paronyms', 'paronym', new_word['paronyms'])
        bulk_insert('Phonetics', 'phonetic', new_word['phonetics'])

        if new_word['examples']:
            db.executemany('INSERT INTO Example (word_id, example, word_class) VALUES (?, ?, ?)', 
                           [(new_word_id, ex['sentence'], ex['word_class']) for ex in new_word['examples']])

        db.commit()

        word_check = {'id': new_word_id, 'uzbek_translation': new_word['uzbek_translation']}
    
    word_id = word_check['id']
    word_details = {
        'paronyms': [row[0] for row in db.execute('SELECT paronym FROM Paronyms WHERE word_id = ?', (word_id,)).fetchall()],
        'definitions': [row[0] for row in db.execute('SELECT definition FROM Definition WHERE word_id = ?', (word_id,)).fetchall()],
        'synonyms': [row[0] for row in db.execute('SELECT synonym FROM Synonym WHERE word_id = ?', (word_id,)).fetchall()],
        'antonyms': [row[0] for row in db.execute('SELECT antonym FROM Antonym WHERE word_id = ?', (word_id,)).fetchall()],
        'examples': [{'sentence': row[0], 'word_class': row[1]} for row in db.execute('SELECT example, word_class FROM Example WHERE word_id = ?', (word_id,)).fetchall()],
        'phonetics': [row[0] for row in db.execute('SELECT phonetic FROM Phonetics WHERE word_id = ?', (word_id,)).fetchall()],
        'definitions_uz': [row[0] for row in db.execute('SELECT definition FROM Definition_uz WHERE word_id = ?', (word_id,)).fetchall()],
        'uzbek_translation': word_check['uzbek_translation']
    }
    if g.history_wordlist:
        if not db.execute('SELECT * FROM wordlist_word WHERE word_id = ? AND wordlist_id = ?', 
                          (word_id, g.history_wordlist['id'])).fetchone():
            db.execute('INSERT INTO wordlist_word (word_id, wordlist_id) VALUES (?, ?)', 
                       (word_id, g.history_wordlist['id']))
            db.commit()
    user_wordlists = db.execute('SELECT * FROM Wordlist WHERE owner_id = ?', (session.get('user_id'),)).fetchall()
    return render_template('word_page.html', 
                           word=word, 
                           word_id=word_id, 
                           word_details=word_details, 
                           image=search_unsplash(word), 
                           wordlists=user_wordlists, 
                           get_examples=get_examples, 
                           audio_url=get_audio_url(word))



@word.route('wordlist/create', methods=['GET', 'POST'])
def create_wordlist():
    if request.method == 'POST':
        title = request.form.get('title')
        db = get_db()
        if not db.execute('SELECT * FROM Wordlist WHERE owner_id = ? AND title = ?', (session.get("user_id"), title)).fetchone():      
            db.execute( "INSERT INTO Wordlist (title, owner_id) VALUES (?, ?)", (title, session.get('user_id')))
            just_created_wordlist_id = db.execute('SELECT * FROM Wordlist WHERE owner_id = ? AND title = ?', (session.get("user_id"), title)).fetchone()
            db.commit()
            return redirect(url_for('word.wordlist_view', id = just_created_wordlist_id['id']))
        else:
            print('Please select another name')
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
            return exceptions.NotFound('NOT AVAIBLE')
    else:
        return exceptions.Forbidden("permessino denied")



@word.route('/my-wordlists')
def my_wordlists():
    if g.user:
        user_wordlists = get_db().execute('SELECT * FROM Wordlist WHERE owner_id = ?', (session.get('user_id'),))
        return render_template('my_wordlists.html', user_wordlists = user_wordlists)
    return redirect(url_for('auth.login'))



@word.route('/delete/<int:id>')
def delete_wordlist(id):
        db = get_db()
        check_if_wordlist = db.execute('SELECT * FROM Wordlist WHERE id = ?', (id,)).fetchone()
        if check_if_wordlist:
            db.execute('DELETE FROM Wordlist WHERE id = ?', (id,))
            db.commit()
            return redirect(url_for('word.my_wordlists'))
        else:
            return jsonify({"success": False, "message": "Wordlist not found."}), 404
        

@word.route('/add_to_wordlist/<int:wordlist_id>/<int:word_id>')
def add_to_wordlist(wordlist_id, word_id):
    db = get_db()
    wordlist = db.execute('SELECT * FROM Wordlist WHERE id = ?', (wordlist_id,)).fetchone()
    if not wordlist:
        return jsonify({"success": False, "message": "Wordlist not found."}), 404
    word = db.execute('SELECT * FROM Word WHERE id = ?', (word_id,)).fetchone()
    if not word:
        return jsonify({"success": False, "message": "Word not found."}), 404
    existing_entry = db.execute(
        'SELECT * FROM wordlist_word WHERE wordlist_id = ? AND word_id = ?', 
        (wordlist_id, word_id)
    ).fetchone()
    if existing_entry:
        return jsonify({"success": False, "message": "Word already exists in the wordlist."}), 400
    db.execute('INSERT INTO wordlist_word (wordlist_id, word_id) VALUES (?, ?)', (wordlist_id, word_id))
    db.commit()
    return redirect(url_for('word.search_word', word = word['word']))


@word.route('/print/<int:wordlist_id>')
def print(wordlist_id):
    db = get_db()
    if db.execute('SELECT * FROM Wordlist WHERE id = ?', (wordlist_id,)).fetchone()['owner_id'] == session.get('user_id'):
        word_ids = db.execute('SELECT * FROM wordlist_word WHERE wordlist_id = ?', (wordlist_id, )).fetchall()
        items = []
        for item in word_ids:
            test = db.execute('SELECT * FROM Word WHERE id = ? ', (item['word_id'], )).fetchone()
            if test:
                items.append(test['word'])
    prm = f"""I will give you my dictionaries in the form of a python list and you will write a special worksheet for your English teacher.
1. You will write a story using all the dictionaries I gave you
WARNING: ALL WORDS MUST BE PARTICIPATED.
2. THE MOST INTERESTING POINT: FROM THE WORDS THAT ARE COMBINED IN YOUR STORY, YOU WILL LEAVE A BLANK SPACE (SUCH AS ____________) IN PLACE OF THE VOCABULARY WORDS I GAVE YOU, THIS IS A HOMEWORK FOR MY STUDENTS.
3. Test part. You will write the definitions of the dictionaries I gave you. My students will look for the one that matches the definition from 4 options.
4.MOST IMPORTANT: YOUR ANSWER MUST BE BASED ON THE PATTERN I GAVE, SO I CAN EASILY EXTRACT IT (BECAUSE I WROTE A SCRIPT TO AUTOMATE IT)
5.STORY MUST BE AT LEAST ( sum of all words * 10)
The pattern you need to follow is:
```html <h2>Story Title</h2>
<hr>
<p>Text here</p>

<!-- Adding spacing using CSS instead of multiple <br> tags -->
<div style="margin-bottom: 20px;"></div>

<h2>Testing</h2>
<!-- Using <ul> for a structured list of questions -->
<section>
    <article>
        <h5>Definition 1</h5>
        <ul>
            <li>A) Variant 1</li>
            <li>B) Variant 2</li>
            <li>C) Variant 3</li>
        </ul>
    </article>

    <article>
        <h5>Definition 2</h5>
        <ul>
            <li>A) Variant 1</li>
            <li>B) Variant 2</li>
            <li>C) Variant 3</li>
        </ul>
    </article>

    <article>
        <h5>Definition 3</h5>
        <ul>
            <li>A) Variant 1</li>
            <li>B) Option 2</li>
            <li>C) Option 3</li>
        </ul>
    </article>
</section>

```
You need to write the html as I show you so that I can print it in weasyprint(python library)
LETS START! my list is: {items}
""" 
    from .tools import extract_data_1 as ex
    html_content = ex(get_gemini_response(prm))
    pdf = HTML(string=html_content).write_pdf()
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=worksheet.pdf'
    return response