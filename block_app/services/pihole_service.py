import requests
from block_app.services.log_service import logger
from block_app.services.database_service import DomainDatabase
from datetime import datetime, timedelta



# Establishing an overall class for Pihole connections
class Pihole:

    # Creating an initialiser class
    def __init__(self, pihole_address, pihole_password):
        self.pihole_address = pihole_address
        self.pihole_password = pihole_password
        self.sid = None
        self.csrf = None
        self.db_domains = DomainDatabase.get_db_domains()


    def authenticate(self):
        try:
            logger.info('Getting SID from Pihole')
            logger.info(f'On address: {self.pihole_address}')
            pihole_response = requests.post(
                f'http://{self.pihole_address}/api/auth',
                json={"password": self.pihole_password},
                timeout = 5
            )

            data_json = pihole_response.json()

            status_code = pihole_response.status_code

            logger.info(f'Status: {status_code} - Data Obtained')

            self.sid = data_json["session"]["sid"]

            self.csrf = data_json["session"]["csrf"]

        except Exception as e:
            logger.exception(f'Exception: {e}')

    def __get_queries(self):
        if self.pihole_sid is None:
            self.authenticate()

        pihole_response = requests.get(
        f'http://{self.pihole_address}/api/queries',
        headers={
            "X-FTL-SID": self.sid,
            "X-FTL-CSRF": self.csrf
            },
        timeout = 5)

        status_code = pihole_response.status_code

        logger.info(f'Status: {status_code} - Data Obtained')

        data_json = pihole_response.json()
        queries = data_json['queries']
        return queries

    # Obtaining Recent Domains
    def __get__recent_domains(self):
        queries = self.__get_queries()


        time_difference = (datetime.now - timedelta(hours=1)).timestamp()


        # Using set method to create object with no duplicates
        domains = set()

        for query in queries:
            if query['time'] >= time_difference:
                domains.add(query['domain'])

        return domains

    # Method for Making Blocked and Non=Blocked List
    def domains_conversion(self):
        pass

# NEED TO:
# Extract RECENT queries (no repetition) - DONE
# Split Blocked and Not-Blocked
# Check with the entries on database (AnalysedDomains)
# If not on Database check:
    # Check Non-blocked entries
    # Checked Blocked entries
# Do Predictions
# Store Predictions
# Retrive Malicious Domains
# If Pihole has List:
    # Update Pihole Block list
# If Pihole has no List:
    # Create a List

