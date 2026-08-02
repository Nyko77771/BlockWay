from threading import Lock
from block_app.services.start_service import StartService
from block_app.services.log_service import logger

lock = Lock()
is_running = False

def start_scheduler(start_service):

    global is_running

    logger.info('Initialing the ML Start Service')

    with lock:

        if is_running:
            logger.info('Scheduler already running')
            return

        scheduler = start_service.start()

        if scheduler.pihole.pihole_address is None:
            logger.warning('Piohole Address not Set')
            return

        scheduler.make_scheduler()
        is_running = True

    logger.info('Starting ML Scan')
    scheduler.start()
