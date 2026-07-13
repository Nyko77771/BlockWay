# Importing Local Services
from block_app.services.pihole_service import Pihole
from block_app.services.database_service import DomainDatabase

from block_app.services.log_service import logger

# Importing Python Libraries
from dotenv import load_dotenv
import os
import time
from datetime import datetime, timedelta

# Importing Scheduler Module to Schedule Hourly Scans:
from scheduler import Scheduler

class StartService:

    # Initialing Method for Class
    def __init__(self, address):
        # Loading environmental variables
        load_dotenv()

        # Obtaining Password from .env
        self.password = os.getenv('PASSWORD')
        # Initialising Pihole class
        self.pihole = Pihole(address, self.password)
        self.database = DomainDatabase()

        # Setting Scheduler variable
        self.schedule = Scheduler()
        # Creating a scheduled job
        self.schedule.hourly(self.run_scan)

    # Method for Starting Scheduled Scans
    def start(self):

        logger.info('Starting Scheduler')

        while True:
            # Executing any given jobs
            self.schedule.exec_jobs()
            # Checking the loop every 10 minutes
            time.sleep(600)

    # Method for Performing Scan
    def run_scan(self):

        logger.info('Starting scheduled ML Analyses')

        try:

            logger.info('Establishing Pihole Connection')
            # Getting SID and CSRF
            self.pihole.authenticate()

            last_scan = self.database.get_last_scan()

            self.permitted_domains, self.blocked_domains = self.pihole.pihole_domain_analyses(last_scan)

            outcome_permmitted = self.pihole.domains_scan(self.permitted_domains)

            outcome_blocked = self.pihole.domains_scan(self.blocked_domains)

            now = datetime.now()
            message = ""
            if outcome_permmitted and outcome_blocked:
                message = "success"
            else:
                message = "failure"

            self.database.update_last_scan(now, message)
        except Exception as e:
            logger.exception('Exception Occurred While Perfoming a Scan')
            logger.exception('Scheduled Scan Failed')





