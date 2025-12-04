import logging
import sys

def configure_logging():
    """
    Configures the root logger with a standard format and stream handler.
    """
    # Create a formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Create a handler that writes to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Remove existing handlers to avoid duplicates if re-configured
    if root_logger.handlers:
        root_logger.handlers.clear()
        
    root_logger.addHandler(handler)

    # Set specific levels for noisy libraries if needed
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
