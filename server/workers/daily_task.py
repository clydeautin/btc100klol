import sys
import logging
from datetime import datetime, timedelta
from server.s3_client import S3ClientFactory
from server.db_accessor import DBAccessor
from openai_files.utils import PromptType
from app import create_app
from server.daily_image_generator import DailyImageGenerator
from openai_files.openai_client import OpenAIClient
from const import AWS_PRESIGNED_URL_EXPIRATION_SECONDS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run():
    logger.info("Starting daily task")
    app = create_app()
    with app.app_context():
        s3_client = S3ClientFactory()
        db_accessor = DBAccessor()

        client = OpenAIClient()

        # This returns a list of holidays for the current date.
        current_date = datetime.now()

        daily_image_generator = DailyImageGenerator(
            openai_client=client,
            s3_client=s3_client,
            db_accessor=db_accessor,
        )

        daily_image_generator.generate_daily_images(
            [PromptType.GENERATE_IMAGE_HAPPY, PromptType.GENERATE_IMAGE_SAD],
            current_date,
            current_date + timedelta(seconds=int(AWS_PRESIGNED_URL_EXPIRATION_SECONDS)),
        )

        logger.info("Daily task completed successfully")


if __name__ == "__main__":
    try:
        run()
    except Exception:
        logger.error("Daily task failed", exc_info=True)
        sys.exit(1)
