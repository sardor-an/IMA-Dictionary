from server.db import init_db
from server import create_app

app = create_app()
# with app.app_context():
#     init_db()
if __name__ == '__main__':
    try:
        app.run(port=9000, debug=True, host='127.0.0.1')
    except Exception as e:
        import logging
        logging.basicConfig(filename='critical_errors.log', level=logging.ERROR)
        logging.error(f"CRITICAL ERROR: {e}", exc_info=True)
        print("A critical error occurred, but the server did not stop.")
