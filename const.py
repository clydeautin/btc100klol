import os
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

DEBUG: bool = True

# OpenAI
DEFAULT_IMAGE_QUALITY: Literal["standard", "hd"] = "standard"
DEFAULT_IMAGE_SIZE: (
    Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] | None
) = "1024x1024"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION")

DEFAULT_IMAGE_URL = "https://static0.gamerantimages.com/wordpress/wp-content/uploads/2021/11/commander-shepard-close-up-mass-effect.jpg"

# 1 day + 5 minutes for overlap
AWS_PRESIGNED_URL_EXPIRATION_SECONDS = 3600 * 24 + 5 * 60
