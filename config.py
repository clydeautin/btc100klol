from dotenv import load_dotenv
import os

load_dotenv()


class Config:

    #Fallback to DATABASE_URL_FIXED if needed for Heroku compatibility
    uri = os.getenv("DATABASE_URL") or os.getenv("DATABASE_URL_FIXED")

    if not uri:
        raise RuntimeError("DATABASE_URL not set")

    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
