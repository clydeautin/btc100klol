from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from const import DEBUG
from pymongo import MongoClient

app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)
client = MongoClient('localhost', 27017)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")




# This is a mongo database, not a postgres database
dbm = client.flask_database

# This is a todos collection in the database
todos = dbm.todos


@app.route("/")
def home():
    return "BTC 100K!"


if __name__ == "__main__":
    app.run(debug=DEBUG, host= '0.0.0.0')
