from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from const import DEBUG

app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)


@app.route("/")
def home():
    return "BTC 100K!"


if __name__ == "__main__":
    app.run(debug=DEBUG)
