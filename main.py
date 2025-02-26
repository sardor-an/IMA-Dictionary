from server.db import init_db
from server import create_app

app = create_app()
# with app.app_context():
#     init_db()
app.run(debug=True)