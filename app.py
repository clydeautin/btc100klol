from flask import Flask

from const import DEBUG

app = Flask(__name__)


@app.route("/")
def home():
    return "BTC 100K!"


if __name__ == "__main__":
    app.run(debug=DEBUG)
