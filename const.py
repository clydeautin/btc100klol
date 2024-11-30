from typing import Literal

DEBUG: bool = True

# OpenAI
DEFAULT_IMAGE_QUALITY: Literal["standard", "hd"] = "standard"
DEFAULT_IMAGE_SIZE: (
    Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] | None
) = "1024x1024"
