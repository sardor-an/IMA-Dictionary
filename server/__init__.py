import os

from flask import Flask, render_template, request, g, redirect, url_for
from .tools import home_page_quote, translate
import logging
def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='123ajsoidu932ejikadk3a',
        DATABASE=os.path.join(app.instance_path, 'server.sqlite'),
        )
    logging.basicConfig(filename='error.log', level=logging.ERROR)
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Catch all exceptions and log them."""
        app.logger.error(f"An error occurred: {e}", exc_info=True)
        return redirect(url_for('home'))
    from . import db
    db.init_app(app)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    from .auth import auth
    from .word import word
    
    app.register_blueprint(auth)
    app.register_blueprint(word)
    

    # home page
    @app.route('/', methods = ['GET', 'POST'])
    # @login_required
    def home():
        g.home_page_quote = home_page_quote
        g.translate = translate
       
        
        if request.method == "POST":
            searched_word = request.form.get("searched_word")
            return redirect(url_for('word.search_word', word=searched_word))

        return render_template('home.html')

    return app
