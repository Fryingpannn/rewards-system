from flask import Flask
from . import routes

app = Flask(__name__)
app.register_blueprint(routes.bp)
# Simulate database
app.db = {}
# In-memory cache (e.g. could be Redis)
app.cache = {}

if __name__ == "__main__":
    app.run(debug=True)