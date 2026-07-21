# Importing os module
import os

# Importing Local Services
from block_app.services.log_service import logger
from block_app.services.ml_model_service import DomainAnalyses
from block_app.services.database_service import DomainDatabase
from block_app.services.pihole_formatter_service import PiholeFormatter

# Importing request library for establishing API communication
import requests

# Importing dataetime for time calculation / conversion
from datetime import datetime, timedelta, timezone

# Importing dotenv library for obtaining values from.env
from dotenv import load_dotenv

# Establishing an overall class for Pihole connections
class Pihole:

    # Creating an initialiser class
    def __init__(self, address=None):

        # Loading .env variables into environment
        load_dotenv()

        # Initialising ML Analysis class
        self.ml_analyses = DomainAnalyses()
        # Initialish Database
        self.database = DomainDatabase()

        if address is None:
            db_pihole_address = self.database.get_pihole_address()

            self.pihole_address = db_pihole_address
        else:
            self.pihole_address = address

        self.pihole_password = os.getenv("PASSWORD")
        self.sid = None
        self.csrf = None

    def contains_address(self):
        if self.pihole_address is None:
            return False
        return True

    # Method for Authenticating with Pihole Connections
    # Used to get SID and
    def authenticate(self):
        try:

            formatter = PiholeFormatter()
            if self.contains_address():

                if formatter.check_address(self.pihole_address): # type: ignore

                    logger.info("Getting SID from Pihole")
                    logger.info(f"On address: {self.pihole_address}")
                    pihole_response = requests.post(
                        f"{str(self.pihole_address).rstrip('/')}/api/auth",
                        json={"password": self.pihole_password},
                        timeout=5,
                    )

                    data_json = pihole_response.json()

                    status_code = pihole_response.status_code

                    logger.info(f"Status: {status_code} - Data Obtained")

                    self.sid = data_json["session"]["sid"]

                    self.csrf = data_json["session"]["csrf"]

        except Exception as e:
            logger.exception(f"Exception: {e}")
            return None

    def __get_queries(self):
        try:
            if self.sid is None:
                self.authenticate()

            if self.sid is None or self.csrf is None:
                logger.error('Not Authenticated with Pihole')
                raise RuntimeError('Pihole Authentication is Not Established')

            logger.info("Getting Pihole Queries")
            logger.info(f"On address: {self.pihole_address}")
            pihole_response = requests.get(
                f"{str(self.pihole_address).rstrip('/')}/api/queries",
                headers={"X-FTL-SID": self.sid, "X-FTL-CSRF": self.csrf},
                timeout=5,
            )

            status_code = pihole_response.status_code

            logger.info(f"Status: {status_code} - Data Obtained")

            data_json = pihole_response.json()
            queries = data_json["queries"]
            return queries
        except RuntimeError:
            logger.exception('No SID or CSRF tokens found')
            return None

    # Obtaining Recent Domains
    def __get__recent_domains(self, last_scan):
        try:
            queries = self.__get_queries()

            if queries is None:
                raise RuntimeError

            logger.info("Getting Recent Queries")
            difference = last_scan.timestamp()

            # Using set method to create object with no duplicates
            domains = set()

            for query in queries:
                if query["time"] >= difference:
                    domains.add(query["domain"])

            return domains
        except RuntimeError:
            logger.exception('No queries obtained found')
            return None


    # Method for Making Blocked and Non=Blocked List
    def __domains_split(self, last_scan):
        try:

            domains = self.__get__recent_domains(last_scan)

            if domains is None:
                raise RuntimeError

            logger.info("Splitting Queries")
            logger.info("Creating Allowed and Blocked Domains")

            blocked_domains = set()
            permited_domains = set()

            for domain in domains:

                status = str(domain["status"])

                status_type = self.__classify_status(status)

                if status_type == "ignore":
                    continue

                if status_type == "block":
                    blocked_domains.add(domain["domain"])
                else:
                    permited_domains.add(domain["domain"])

            return permited_domains, blocked_domains
        except RuntimeError:
            logger.exception('No domains in queries')
            return None

    # Determine Status Type of Query
    def __classify_status(self, status):

        blocked_status = ["GRAVITY"]
        allowed_status = ["FORWARDED", "CACHE", "CACHE_STALE"]
        in_progress_status = ["IN_PROGRESS"]

        if status in in_progress_status:
            return "ignore"

        if status in blocked_status:
            return "block"

        if status in allowed_status:
            return "allow"

    def get_status(self, status):
        return self.__classify_status(status)

    # Method for Finding Newly Encountered Domains
    def pihole_domain_analyses(self, last_scan):

        logger.info("Obtaining Unfamiliar Domains")

        db_domains = self.database.get_db_domains()


        permitted_domains, blocked_domains = self.__domains_split(last_scan) # type: ignore


        unfamiliar_permitted_domains = self.__get_new_domains(
            permitted_domains, db_domains
        )

        unfamiliar_blocked_domains = self.__get_new_domains(blocked_domains, db_domains)

        return unfamiliar_permitted_domains, unfamiliar_blocked_domains

        self.perform_ml_analyses(unfamiliar_permitted_domains, "allowed")
        self.perform_ml_analyses(unfamiliar_blocked_domains, "blocked")

    # Database Retrieval
    # ML Analysis Preparation
    def __get_new_domains(self, pi_domains, db_domains):

        to_analyse = set()

        for domain in pi_domains:
            if domain not in db_domains:
                to_analyse.add(domain)

        return to_analyse

    def get_recent_pihole_domains(self):
        try:
            logger.info("Obtaining Recent Pihole Domains")

            last_scan = self.database.get_last_scan()

            return self.__get__recent_domains(last_scan)
        except Exception:
            logger.exception('Unable to Obtain Recent Domains')
            return None

    # Method for Performing Scan
    def domains_scan(self, domains):
        try:
            logger.info(f"Starting domain scan for {domains} ; size: {len(domains)}")
            for domain in domains:
                logger.info(f"Scanning {domain}")

                logistic_probability = self.ml_analyses.logistic_probability(domain)

                if logistic_probability < 60:
                    logger.info("Logiistic Model Determined Domain to be Benign")
                    logistic_prediction = self.ml_analyses.logistic_prediction(domain)
                    self.database.add_db_domain(domain, "benign", logistic_prediction)
                else:
                    # Analysing with better model
                    logger.info("Random Forrest Scan is Required")
                    random_forrest_prediction = (
                        self.ml_analyses.random_forrest_prediction(domain)
                    )

                    # If score is high than likely Malicious
                    if random_forrest_prediction >= 80:

                        self.add_to_pihole_blocklist(domain)
                        self.database.add_db_domain(
                            domain, "malicious", random_forrest_prediction, True
                        )
                    else:
                        logistic_prediction = self.ml_analyses.logistic_prediction(
                            domain
                        )
                        self.database.add_db_domain(
                            domain, "benign", logistic_prediction
                        )

                logger.info("Scan Completed")
            logger.info(f"Domains {domains} have been scanned")
            return True
        except Exception:
            logger.exception("Exxception Occurred while Performing a Scan")

    def add_to_pihole_blocklist(self, domain):
        pass

    #################################################

    # General Pihole Information:
    # Get Pihole's Statistical Data for Later Display
    def get_pihole_summary(self):

        if self.sid is None or self.csrf is None:
            self.authenticate()

        if self.sid is None or self.csrf is None:
            logger.error('Not Authenticated with Pihole')
            logger.info(f'Pihole address is: {self.pihole_address}')
            raise RuntimeError('Pihole Authentication is Not Established')

        logger.info("Getting Pihole Database Summary")

        current_time = datetime.now(timezone.utc).timestamp()

        hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()

        pihole_response = requests.get(
            f"http://{self.pihole_address}/api/stats/database/summary",
            headers={
                "X-FTL-SID": self.sid, "X-FTL-CSRF": self.csrf
                },
            params={
                "from": str(hour_ago),
                "until": str(current_time)},
            timeout=5,
        )

        summary = pihole_response.json()

        return summary

    # Method for Getting Blocked Clients from Pihoole / Database
    def get_recent_blocked_clients(self):

        if self.sid is None or self.csrf is None:
            self.authenticate()

        if self.sid is None or self.csrf is None:
            logger.error('Not Authenticated with Pihole')
            raise RuntimeError('Pihole Authentication is Not Established')

        logger.info("Getting Pihole Top Clients")

        # Getting Pihole Queries
        queries = self.__get_queries()

        pihole_events = []

        if queries is not None:

            for query in queries:

                status = self.__classify_status(query["status"])

                if status is not "block":
                    continue


                pihole_events.append(
                    {
                        "time": query["time"],
                        "domain": query['domain'],
                        "source": 'Pihole'
                    }
                )

        # Getting Domains from Database
        from_time = (datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()
        until_time = datetime.now(timezone.utc).timestamp()
        recent_db_domains = self.database.get_db_recent_domains(from_time, until_time)

        if recent_db_domains is None and queries is not None:
            pihole_events.sort(
                reverse = True,
                key = lambda event : event["time"]
            )
            return pihole_events[:5]

        if recent_db_domains is None and queries is None:
            logger.warning('No domains obtained from Pihole and database.')
            return None

        ml_events = []

        if recent_db_domains is not None:
            for domain in recent_db_domains:
                ml_events.append(
                    {
                        "time": domain.date_created.timestamp(),
                        "domain": domain.domain_name,
                        "source": 'BlockWay ML'
                    }
                )

        events = pihole_events + ml_events
        events.sort(
            reverse = True,
            key = lambda event : event["time"]
        )

        return events[:5]

