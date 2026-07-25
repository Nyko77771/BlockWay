# Importing threading module
import threading

# Importing ML Generating Method
from block_app.services.run_ml_start_service import start_scheduler

# Importing Logger
from block_app.services.log_service import logger

class MLThreadManager:

    has_started = False

    @classmethod
    def start(cls):
        logger.info("MLThreadManager.start begun")

        logger.info("State os ML Thread Manager: %s", cls.has_started)
        if cls.has_started:
            logger.info("ML Thread is Runnning")
            return

        # Performing ML Analyses
        # Using Threadding to run ML scan concurrently
        thread = threading.Thread(target=run, daemon=True)

        thread.start()
        cls.has_started = True
        logger.info("Starting ML Thread")

def run():
    try:
        start_scheduler()
    except Exception:
        logger.exception("ML Scheduler not working")