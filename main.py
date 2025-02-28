from flask import Flask
from api import routes

app = Flask(__name__)
app.register_blueprint(routes.bp)
# Simulate database
db = {}

if __name__ == "__main__":
    app.run(debug=True)