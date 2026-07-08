# Importing Local Services
from block_app.services.log_service import logger
from block_app.services.database_service import DomainDatabase

# Importing request library for establishing API communication
import requests
# Importing dataetime for time calculation / conversion
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

    # Method for Authenticating with Pihole Connections
    # Used to get SID and
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

        logger.info('Getting Pihole Queries')
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

        logger.info('Getting Recent Queries')
        time_difference = (datetime.now - timedelta(hours=1)).timestamp()


        # Using set method to create object with no duplicates
        domains = set()

        for query in queries:
            if query['time'] >= time_difference:
                domains.add(query['domain'])

        return domains

    # Method for Making Blocked and Non=Blocked List
    def __domains_split(self):
        domains = self.__get__recent_domains()

        logger.info('Splitting Queries')
        logger.info('Creating Allowed and Blocked Domains')

        blocked_domains = set()
        permited_domains = set()

        for domain in domains:

            status = str(domain['status'])

            status_type = self.__classify_status(status)

            if status_type == 'ignore':
                continue

            if  status_type == 'block':
                blocked_domains.add(domain['domain'])
            else:
                permited_domains.add(domain['domain'])

        return permited_domains, blocked_domains

    # Determine Status Type of Query
    def __classify_status(self, status):

        blocked_status = ['GRAVITY']
        allowed_status = ['FORWARDED', 'CACHE', 'CACHE_STALE']
        in_progress_status = ['IN_PROGRESS']

        if status in in_progress_status:
            return 'ignore'

        if status in blocked_status:
            return 'block'

        if status in allowed_status:
            return 'allow'


    # Method for Finding Newly Encountered Domains
    def pihole_domain_analyses(self):

        logger.info('Obtaining Unfamiliar Domains')

        db_domains = DomainDatabase.get_db_domains()

        permitted_domains, blocked_domains = self.__domains_split()

        unfamiliar_permitted_domains = self.__get_new_domains(permitted_domains, db_domains)

        unfamiliar_blocked_domains = self.__get_new_domains(blocked_domains, db_domains)

        return unfamiliar_permitted_domains, unfamiliar_blocked_domains

        self.perform_ml_analyses(unfamiliar_permitted_domains, 'allowed')
        self.perform_ml_analyses(unfamiliar_blocked_domains, 'blocked')


    # Database Retrieval
    # ML Analysis Preparation
    def __get_new_domains(self, pi_domains, db_domains):

        to_analyse = set()

        for domain in pi_domains:
            if domain not in db_domains:
                to_analyse.append(domain)

        return to_analyse


    #################################################


    # General Pihole Information:
    # Get Pihole's Statistical Data for Later Display
    def get_pihole_summary(self):

        if self.pihole_sid is None:
            self.authenticate()

        logger.info('Getting Pihole Database Summary')

        current_time = datetime.now().timestamp()

        hour_ago = (datetime.now - timedelta(hours=1)).timestamp()

        pihole_response = requests.get(
        f'http://{self.pihole_address}/api/stats/database/summary',
        headers={
            "X-FTL-SID": self.sid,
            "X-FTL-CSRF": self.csrf
            },
        params={
            "from": str(hour_ago),
            "until": str(current_time)
        },
        timeout = 5)

        summary = pihole_response.json()

        return summary







# NEED TO:
# Extract RECENT queries (no repetition) - DONE
# Split Blocked and Not-Blocked - DONE
# Check with the entries on database  (AnalysedDomains) - DONE
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

