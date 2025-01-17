""" Generic worker because we don't want to pay for additional dynos we don't need """

from apscheduler.schedulers.blocking import BlockingScheduler  # type: ignore
from datetime import datetime

from facades.cmc_facade import get_btc_price
from openai_files.helpers import get_prompt, get_system_message
from openai_files.openai_client import OpenAIClient
from openai_files.utils import PromptType
from server.s3_client import S3ClientFactory

SESSION_BATCH_SIZE = 10

scheduler = BlockingScheduler()


# 5 - minute worker
# check to see if there is a task in the queue
# tasks:
# check price of bitcoin and write
@scheduler.scheduled_job("interval", minutes=5)
def check_bitcoin_price() -> None:
    # get API credentials or API client
    # get_btc_price
    price = get_btc_price()
    # some validation of price
    # write to DB
    return price


# Daily worker
# check the date
# get the holidays for the date
# generate the prompts for the the day
# generate the images for the day
# save the images to S3
# generate pre-signed URLs that expire in 25 hours.
# save pre-signed URLs
@scheduler.scheduled_job("cron", hour=0, minute=1, timezone="America/Los_Angeles")
def daily_image_generation() -> None:
    s3_client = S3ClientFactory()
    client = OpenAIClient()

    holiday_list = client.fetch_holiday_list()
    holiday_image_prompt = get_prompt(PromptType.GENERATE_IMAGE_HAPPY, holiday_list)
    print(holiday_image_prompt)
    holiday_image_url = client.fetch_generated_image_url(holiday_image_prompt)
    print(holiday_image_url)
    curr_date_str = datetime.now().strftime("%d-%b-%Y").upper()
    file_name = f"{PromptType.GENERATE_IMAGE_HAPPY.value}-{curr_date_str}"
    u_file_name = client.generate_unique_file_name(file_name)
    s3_image_url = s3_client.save_image_to_s3(holiday_image_url, u_file_name)
    print(f"{s3_image_url=}")
    pre_signed_url = s3_client.fetch_presigned_url(u_file_name)
    print(f"{pre_signed_url=}")
    # write pre_signed_url x 2 to DB.

    # image table will be like:
    # date, type, prompt_id, s3_url, pre_signed_url (this may change)

    # process could be, check latest btc price from db, if > 100k, get latest image where type == 'happy'

    # alternate thought: daily_version table: date, image_happy_id, image_sad_id, active (bool)
    # process is check for latest active daily_version and serve appropriate image.
    ...
