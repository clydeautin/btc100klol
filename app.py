from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv
import os
import logging
from app import db

# Import our custom modules
from facades.cmc_facade import get_btc_price, CMCApiError
from server.db_accessor import DBAccessor
from server.models.daily_image_version import DailyImageVersion
from server.models.utils import TaskStatus
from openai_files.utils import PromptType
from const import DEFAULT_IMAGE_URL

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database outside of create_app to avoid circular imports


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")
    db.init_app(app)

    # Create application context for database operations
    with app.app_context():
        pass

    @app.route("/")
    def home():
        # Check if we're in demo mode (no API keys)
        if not os.getenv("CMC_API_KEY"):
            return demo_mode()

        try:
            # Get current Bitcoin price
            btc_price = get_btc_price()
            logger.info(f"Fetched BTC price: ${btc_price:,.2f}")

            # Determine which image type to show based on price
            is_above_100k = btc_price >= 100000
            target_prompt_type = (
                PromptType.GENERATE_IMAGE_HAPPY
                if is_above_100k
                else PromptType.GENERATE_IMAGE_SAD
            )

            # Get the appropriate image from database
            image_url = get_current_image(target_prompt_type)

            # Determine the message
            if is_above_100k:
                message = "🚀 Bitcoin is above $100K! Time to celebrate! 🎉"
            else:
                message = (
                    f"😅 Bitcoin is at ${btc_price:,.2f} - Still waiting for $100K..."
                )

            return render_template(
                "index.html",
                message=message,
                price=btc_price,
                image_url=image_url,
                is_above_100k=is_above_100k,
            )

        except CMCApiError as e:
            logger.error(f"Failed to fetch Bitcoin price: {e}")
            return render_template(
                "index.html",
                message="⚠️ Unable to fetch current Bitcoin price",
                price="N/A",
                image_url=DEFAULT_IMAGE_URL,
                is_above_100k=False,
                error="Price data temporarily unavailable",
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return render_template(
                "index.html",
                message="⚠️ Something went wrong",
                price="N/A",
                image_url=DEFAULT_IMAGE_URL,
                is_above_100k=False,
                error="Service temporarily unavailable",
            )

    @app.route("/health")
    def health_check():
        """Simple health check endpoint"""
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}

    return app


def demo_mode():
    """Demo mode when API keys are not available"""
    import random
    from flask import url_for

    # Simulate different Bitcoin prices for demo
    demo_prices = [85000, 95000, 102000, 110000, 125000]
    demo_price = random.choice(demo_prices)

    is_above_100k = demo_price >= 100000

    # Use specific images based on price
    if is_above_100k:
        message = "🚀 Bitcoin is above $100K! Time to celebrate! 🎉"
        try:
            image_url = url_for(
                "static", filename="images/happy_investor_btc100k_lol.png"
            )
        except:
            image_url = DEFAULT_IMAGE_URL
    else:
        message = f"😅 Bitcoin is at ${demo_price:,.2f} - Still waiting for $100K..."
        try:
            image_url = url_for(
                "static", filename="images/sad_investor_btc100k_lol.png"
            )
        except:
            image_url = DEFAULT_IMAGE_URL

    return render_template(
        "index.html",
        message=message + " (Demo Mode)",
        price=demo_price,
        image_url=image_url,
        is_above_100k=is_above_100k,
        demo_mode=True,
    )


def get_current_image(prompt_type: PromptType) -> str:
    """
    Get the current active image URL for the specified prompt type.
    Falls back to local images, then default image if no active image is found.
    """
    try:
        db_accessor = DBAccessor()

        # Query for the most recent active image of the specified type
        latest_version = (
            db_accessor.query(DailyImageVersion)
            .filter(
                DailyImageVersion.prompt_type == prompt_type,
                DailyImageVersion.is_active == True,
                DailyImageVersion.status == TaskStatus.COMPLETED,
                DailyImageVersion.presigned_url.isnot(None),
                DailyImageVersion.presigned_url_expiry > datetime.now(),
            )
            .order_by(DailyImageVersion.prompt_date.desc())
            .first()
        )

        if latest_version and latest_version.presigned_url:
            logger.info(f"Found active image for {prompt_type.value}")
            return latest_version.presigned_url
        else:
            logger.warning(
                f"No active image found for {prompt_type.value}, using local images"
            )
            # Fall back to local images
            from flask import url_for

            if prompt_type == PromptType.GENERATE_IMAGE_HAPPY:
                try:
                    return url_for(
                        "static", filename="images/happy_investor_btc100k_lol.png"
                    )
                except:
                    pass
            elif prompt_type == PromptType.GENERATE_IMAGE_SAD:
                try:
                    return url_for(
                        "static", filename="images/sad_investor_btc100k_lol.png"
                    )
                except:
                    pass
            return DEFAULT_IMAGE_URL

    except Exception as e:
        logger.error(f"Error fetching image for {prompt_type.value}: {e}")
        # Fall back to local images on error
        from flask import url_for

        try:
            if prompt_type == PromptType.GENERATE_IMAGE_HAPPY:
                return url_for(
                    "static", filename="images/happy_investor_btc100k_lol.png"
                )
            elif prompt_type == PromptType.GENERATE_IMAGE_SAD:
                return url_for("static", filename="images/sad_investor_btc100k_lol.png")
        except:
            pass
        return DEFAULT_IMAGE_URL


if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", 5001))
    print(f"🚀 Starting BTC 100K LOL on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
