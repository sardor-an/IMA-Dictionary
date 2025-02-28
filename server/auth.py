import functools

from flask import Blueprint, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from server.db import get_db
auth = Blueprint('auth', __name__, url_prefix='/auth')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        if not first_name or not last_name or not email or not password:
            error = "All fields are required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif db.execute("SELECT id FROM user WHERE email = ?", (email,)).fetchone():
            error = "This email is already registered."

        if error:
            print(f"ERROR: {error}")
            return redirect(url_for("auth.register"))

        db.execute(
            "INSERT INTO user (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
            (first_name, last_name, email, generate_password_hash(password)),
        )
        just_registered_user = db.execute('SELECT * FROM User WHERE email = ?', (email, )).fetchone()

        db.execute('INSERT INTO Wordlist (title, owner_id) VALUES (?, ?)', ('History', just_registered_user['id']))
        db.commit()

        print("SUCCESS: Registration successful! You can now log in.")  
        return redirect(url_for("auth.login"))

    return render_template('auth/register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute("SELECT * FROM user WHERE email = ?", (email,)).fetchone()
        if not email or not password:
            error = "All fields are required."
        elif user is None:
            error = "No account found with this email."
        elif not check_password_hash(user["password"], password): 
            error = "Incorrect password."
        if error:
            print(f"ERROR: {error}")
            return redirect(url_for("auth.login"))

        session["user_id"] = user["id"]
        g.history_wordlist = get_db().execute("SELECT * FROM Wordlist WHERE owner_id = ? AND title = ?", (session.get('user_id',), 'History')).fetchone()
        print("SUCCESS: Login successful! Welcome back.")
        return redirect(url_for("home"))

    return render_template('auth/login.html')



@auth.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
      g.user = None  
      g.history_wordlist = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
        g.history_wordlist = get_db().execute("SELECT * FROM Wordlist WHERE owner_id = ? AND title = ?", (session.get('user_id',), 'History')).fetchone()


@auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view