from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL_FIXED", "postgresql://postgres@localhost/btc_dev"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
