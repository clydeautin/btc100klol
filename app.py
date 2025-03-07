from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from const import DEBUG
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.config.from_object("config.Config")
db = SQLAlchemy(app)

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
mongo_db_name = os.getenv("MONGO_DB")

# initialize mongoDB client and database
client = MongoClient(mongo_uri)
# This is a mongo database, not a postgres database
# dbm = client[mongo_db_name]


@app.route("/")
def home():
    return "BTC 100K!"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# These are controller actions related to MongoDB to test if it works properly
# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         content = request.form["content"]
#         degree = request.form["degree"]
#         dbm["todos"].insert_one({"content": content, "degree": degree})
#         return redirect(url_for("index"))
#     all_todos = dbm["todos"].find()
#     return render_template("index.html", todos=all_todos)

# @app.post("/<id>/delete/")
# def delete(id):
#     dbm["todos"].delete_one({"_id": ObjectId(id)})
#     return redirect(url_for("index"))

# # This is a todos collection in the database
# todos = dbm.todos
