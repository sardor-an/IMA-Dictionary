import os

from flask import Flask, render_template, request, g, redirect, url_for
from .tools import home_page_quote, translate

def create_app():
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='123ajsoidu932ejikadk3a',
        DATABASE=os.path.join(app.instance_path, 'server.sqlite'),
    )

    

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    from . import db
    from .auth import auth
    from .word import word

    app.register_blueprint(auth)
    app.register_blueprint(word)




    db.init_app(app)

    # home page
    @app.route('/', methods = ['GET', 'POST'])
    def home():
        g.home_page_quote = home_page_quote
        g.translate = translate
        
        if request.method == "POST":
            searched_word = request.form.get("searched_word")
            return redirect(url_for('word.search_word', word=searched_word))



        return render_template('home.html')

    return app
