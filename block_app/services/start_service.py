# Importing Local Services
from block_app.services.pihole_service import Pihole
from block_app.services.database_service import DomainDatabase

from block_app.services.log_service import logger

# Importing Python Libraries
from dotenv import load_dotenv
import os
import time

# Importing Scheduler Module to Schedule Hourly Scans:
from scheduler import Scheduler

# Importing datetime
import datetime

class StartService:

    # Initialing Method for Class
    def __init__(self, pihole_service):

        # Loading environmental variables
        load_dotenv()

        # Initialing the Database
        self.database = DomainDatabase()
        address = self.database.get_pihole_address()
        # Obtaining Password from .env
        self.password = os.getenv('PASSWORD')
        # Initialising Pihole class
        self.pihole = pihole_service
        # Setting Scheduler variable
        self.schedule = Scheduler()
        # Variable for tracking self scan
        self.scanning = False

    def make_scheduler(self):
        # Creating a scheduled job
        self.schedule.minutely(datetime.time(second=10),self.run_scan)

    # Method for Starting Scheduled Scans
    def start(self):

        logger.info('Starting Scheduler')

        # Running Initial Scan
        self.run_scan()

        while True:
            # Executing any given jobs
            self.schedule.exec_jobs()
            # Checking the loop every 10 minutes
            # Change to 1 for Presentation Purpose
            time.sleep(1)

    # Method for Performing Scan
    def run_scan(self):

        if self.scanning:
            logger.warning('Scan is Running')
            return
        self.scanning = True

        logger.info('##### Starting scheduled ML Analyses ######')

        try:

            logger.info('Establishing Pihole Connection')
            # Getting SID and CSRF
            self.pihole.authenticate()

            last_scan = self.database.get_last_scan()

            self.permitted_domains, self.blocked_domains = self.pihole.pihole_domain_analyses(last_scan)

            outcome_permmitted = self.pihole.domains_scan(self.permitted_domains)

            outcome_blocked = self.pihole.domains_scan(self.blocked_domains)

            message = ""

            if outcome_permmitted and outcome_blocked:
                message = "success"
            else:
                message = "failure"

            self.database.update_last_scan(message)
        except Exception:
            logger.exception('Exception Occurred While Perfoming a Scan')
            logger.exception('Scheduled Scan Failed')
