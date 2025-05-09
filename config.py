from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    uri = os.getenv(
        "DATABASE_URL_FIXED", "postgresql://johnyamashiro@localhost/btc_dev"
    )  # "postgresql://postgres@localhost/btc_dev")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
