# Importing os module
import os

# Importing time module
import time

# Importing Local Services
from block_app.services.log_service import logger
from block_app.services.ml_model_service import DomainAnalyses
from block_app.services.database_service import DomainDatabase
from block_app.services.pihole_formatter_service import PiholeFormatter
from block_app.services.pihole_connection_service import PiholeConnectionChecker

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
        # Initialising Requests Sessions
        self.session = requests.Session()

        # Adding Caching to Pihole
        self.cache = {}
        self.cache_duration = 120

        if address is None:
            db_pihole_address = self.database.get_pihole_address()

            self.pihole_address = db_pihole_address
        else:
            self.pihole_address = str(address).rstrip("/")
        logger.info(f"PIHOLE ADDRESS ADDED: {self.pihole_address}")

        self.pihole_password = os.getenv("PASSWORD")
        self.connectionn_checker = PiholeConnectionChecker(self)
        # Caching for Authentication
        self.sid = None
        self.csrf = None
        self.authentication_period = None
        self.authentication_cache_period = 300

    def contains_address(self):
        if self.pihole_address is None:
            return False
        return True

    def get_address(self):
        return self.database.get_pihole_address()

    # Method for Checking Connection Cache
    # Used for Preventing Too Many Connections to Client (Pihole)
    def get_cache_data(self, name, method, duration_time=None, *args, **kwargs):

        current_time = time.time()

        if duration_time is None:
            duration = self.cache_duration
        else:
            duration = duration_time

        # If cached name of program is found
        if name in self.cache:
            # Get the cached method
            cached_item = self.cache[name]
            # If cached time is less than the scheduled time
            # then retrieve the cached item
            if current_time - cached_item["time"] < duration:
                return cached_item["data"]

        # If no cached method found
        # Create data variable linked to function
        data = method(*args, **kwargs)

        # Add new cached item to cache list
        self.cache[name] = {"data": data, "time": current_time}

        # Returning the function if the cached program is ont found
        # Or the time expired
        return data

    # Creating Custom Method for Generating Requests
    def __make_request(self, method, api_destination, params=None, json=None):

        # Establishing Authentication
        if self.sid is None or self.csrf is None:
            self.authenticate()

        if self.sid is None or self.csrf is None:
            logger.error("Not Authenticated with Pihole")
            raise RuntimeError("Pihole Authentication is Not Established")

        headers = {"X-FTL-SID": self.sid, "X-FTL-CSRF": self.csrf}

        response = self.session.request(
            method=method,
            url=f"{str(self.pihole_address).rstrip('/')}/{str(api_destination).lstrip('/')}",
            headers=headers,
            params=params,
            json=json,
            timeout=5,
        )

        status_code = response.status_code
        logger.info(f"Status Code: {status_code}")
        if status_code == 401:
            logger.info("Pihole Session Expired")

            self.sid = None
            self.csrf = None
            self.authenticate()

            if self.sid is None or self.csrf is None:
                logger.error("Not Authenticated with Pihole")
                raise RuntimeError("Pihole Authentication is Not Established")

            headers = {"X-FTL-SID": self.sid, "X-FTL-CSRF": self.csrf}

            response = self.session.request(
                method=method,
                url=f"{str(self.pihole_address).rstrip('/')}/{str(api_destination).lstrip('/')}",
                headers=headers,
                params=params,
                json=json,
                timeout=5,
            )

        logger.info("Data Obtained")
        return response.json()

    # Method for Authenticating with Pihole Connections
    # Used to get SID and
    def authenticate(self):
        try:

            current_time = time.time()
            if self.authentication_period:
                difference = current_time - self.authentication_period

                if (
                    self.sid
                    and self.csrf
                    and difference < self.authentication_cache_period
                ):
                    logger.info("Using Existing Pihole Details")
                    return

            formatter = PiholeFormatter()

            if not self.contains_address():
                raise RuntimeError("Pihole address is missing and not configured")

            if formatter.check_address(self.pihole_address):  # type: ignore

                logger.info("Authenticating with Pihole")
                logger.info(f"On address: {self.pihole_address}")

                pihole_response = self.session.post(
                    f"{str(self.pihole_address).rstrip('/')}/api/auth",
                    json={"password": self.pihole_password},
                    timeout=5,
                )

                data_json = pihole_response.json()

                logger.info(f"Pi-hole Auth Status: {pihole_response.status_code}")

                if "session" not in data_json:
                    logger.error("Pihole authentication failed")
                    raise RuntimeError("Pihole authentication failed")

                self.sid = data_json["session"]["sid"]

                self.csrf = data_json["session"]["csrf"]

                self.authentication_period = current_time

        except Exception as e:
            logger.exception(f"Authentication failure: {e}")
            self.sid = None
            self.csrf = None
            self.authentication_period = None
            raise

    # Method for obtaining the Queries from Pihole
    def __get_queries(self):
        try:
            if self.sid is None:
                self.authenticate()

            if self.sid is None or self.csrf is None:
                logger.error("Not Authenticated with Pihole")
                raise RuntimeError("Pihole Authentication is Not Established")

            logger.info("Getting Pihole Queries")
            logger.info(f"On address: {self.pihole_address}")

            data_json = self.__make_request(method="GET", api_destination="api/queries")

            queries = data_json["queries"]
            return queries

        except RuntimeError:
            logger.exception("No SID or CSRF tokens found")
            raise

    # Obtaining Recent Domains Names
    def __get__recent_domains(self, last_scan):
        try:

            queries = self.get_cache_data(
                name="recent_domains", method=self.__get_queries, duration_time=60
            )

            if not queries:
                raise RuntimeError

            logger.info("Getting Recent Queries")

            if last_scan is None:
                logger.info("No previous scan found. Getting all recent domains.")
                difference = 86300
            else:
                difference = last_scan.timestamp()

            # Using set method to create object with no duplicates
            domains = set()

            for query in queries:
                if query["time"] >= difference:
                    domains.add(query["domain"])

            return domains
        except RuntimeError:
            logger.exception("No queries obtained found")
            return set()

    # Method for Obtaining the Domains with Status
    def __get_recent_domains_status(self, last_scan):

        try:
            queries = self.get_cache_data(
                name="recent_domains", method=self.__get_queries, duration_time=40
            )

            if not queries:
                logger.warning("Nothing in queries")

            logger.info("Getting Recent Queries")
            if last_scan is None:
                logger.info("No previous scan found. Getting all recent domains.")
                difference = 86300
            else:
                difference = last_scan.timestamp()

            # Using set method to create object with no duplicates
            domains = []

            for query in queries:
                if query["time"] >= difference:
                    domains.append(
                        {"domain": query["domain"], "status": query["status"]}
                    )
            return domains
        except RuntimeError:
            logger.exception("No queries obtained found")
            return []

    # Method for Making Blocked and Non=Blocked List
    def __domains_split(self, last_scan):
        try:

            domains = self.__get_recent_domains_status(last_scan)

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
            logger.exception("No domains in queries")
            return set(), set()

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

        permitted_domains, blocked_domains = self.__domains_split(last_scan)  # type: ignore

        unfamiliar_permitted_domains = self.__get_new_domains(
            permitted_domains, db_domains
        )

        unfamiliar_blocked_domains = self.__get_new_domains(blocked_domains, db_domains)

        return unfamiliar_permitted_domains, unfamiliar_blocked_domains

    # Database Retrieval
    # ML Analysis Preparation
    def __get_new_domains(self, pi_domains, db_domains):

        to_analyse = set()

        for domain in pi_domains:
            if domain not in db_domains:
                to_analyse.add(domain)

        return to_analyse

    # Method for Obtaining Recent Domains with Status
    def get_recent_pihole_domains(self):
        try:
            logger.info("Obtaining Recent Pihole Domains")

            last_scan = self.database.get_last_scan()
            if last_scan is None:
                logger.error("No ML details found")
                last_scan = datetime.now(timezone.utc) - timedelta(hours=24)
            return self.__get_recent_domains_status(last_scan)
        except Exception as e:
            logger.exception("Unable to Obtain Recent Domains")
            logger.exception(f"{e}")
            return None

    # Method for Obtaining all of the Domains
    def __get_all_domains(self):

        data_json = self.__make_request(method="GET", api_destination="api/domains")

        return data_json["domains"]

    # Method for Performing Scan
    def domains_scan(self, domains):
        try:
            logger.info(f"ML SCAN STARTED - Domains received: {domains}")
            logger.info(f"Starting domain scan for {domains} ; size: {len(domains)}")
            for domain in domains:
                logger.info(f"Scanning {domain}")

                logistic_probability = self.ml_analyses.logistic_probability(domain)

                if logistic_probability is None:
                    continue

                if logistic_probability < 0.60:
                    logger.info("Logiistic Model Determined Domain to be Benign")
                    logistic_prediction = self.ml_analyses.logistic_prediction(domain)
                    self.database.add_db_domain(
                        domain, "benign", logistic_prediction, is_string=True
                    )
                else:
                    # Analysing with better model
                    logger.info("Random Forrest Scan is Required")
                    random_forrest_probability = (
                        self.ml_analyses.random_forrest_probability(domain)
                    )

                    if random_forrest_probability is None:
                        continue

                    # If score is high than likely Malicious
                    if random_forrest_probability >= 0.80:

                        self.add_to_block_pihole_blocklist(domain)
                        self.database.add_db_domain(
                            domain, "malicious", random_forrest_probability, True
                        )
                    else:
                        self.database.add_db_domain(
                            domain, "benign", random_forrest_probability, is_string=True
                        )

                logger.info("Scan Completed")
            logger.info(f"Domains {domains} have been scanned")
            return True
        except Exception:
            logger.exception("Exxception Occurred while Performing a Scan")

    # Method for Adding to Pihole
    # Adds as a Domain to be Blocked
    def add_to_block_pihole_blocklist(self, domain):

        if self.sid is None or self.csrf is None:
            self.authenticate()

        if self.sid is None or self.csrf is None:
            logger.error("Not Authenticated with Pihole")
            logger.info(f"Pihole address is: {self.pihole_address}")
            raise RuntimeError("Pihole Authentication is Not Established")

        if not self.check_pihole_domain(domain):
            logger.info("Adding Blocked Domain to Pihole")
            pihole_response = self.session.post(
                f"{str(self.pihole_address).rstrip('/')}/api/domains/deny/exact",
                headers={
                    "X-FTL-SID": self.sid,
                    "X-FTL-CSRF": self.csrf,
                },
                json={
                    "domain": domain,
                },
                timeout=5,
            )

            if pihole_response.status_code in (200, 201):
                logger.info(f"Added {domain} to Pihole")
                return True

            logger.error("Unable to Add Domain to Pihole: " f"{pihole_response.text}")
            return False
        logger.info("Domain Already Exists")
        return False

    # Method for Adding to Pihole
    # Adds as a Domain to be Allowed
    def add_to_allow_pihole_blocklist(self, domain):

        if self.sid is None or self.csrf is None:
            self.authenticate()

        if self.sid is None or self.csrf is None:
            logger.error("Not Authenticated with Pihole")
            logger.info(f"Pihole address is: {self.pihole_address}")
            raise RuntimeError("Pihole Authentication is Not Established")

        if not self.check_pihole_domain(domain):
            logger.info("Adding Allow Domain to Pihole")
            pihole_response = self.session.post(
                f"{str(self.pihole_address).rstrip('/')}/api/domains/allow/exact",
                headers={
                    "X-FTL-SID": self.sid,
                    "X-FTL-CSRF": self.csrf,
                },
                json={
                    "domain": domain,
                },
                timeout=5,
            )

            if pihole_response.status_code in (200, 201):
                logger.info(f"Added {domain} to Pihole")
                return True

            logger.error("Unable to Add Domain to Pihole: " f"{pihole_response.text}")
            return False
        logger.info("Domain Already Exists")
        return False

    # Method for Deleting a Domain
    def delete_pihole_domain(self, domain):

        if self.sid is None or self.csrf is None:
            self.authenticate()

        if self.sid is None or self.csrf is None:
            logger.error("Not Authenticated with Pihole")
            logger.info(f"Pihole address is: {self.pihole_address}")
            raise RuntimeError("Pihole Authentication is Not Established")

        logger.info("Updating Pihole Domain")

        domain_type = ["allow", "deny"]

        for type in domain_type:

            pihole_response = self.session.delete(
                f"{str(self.pihole_address).rstrip('/')}/api/domains/{type}/exact/{domain}",
                headers={
                    "X-FTL-SID": self.sid,
                    "X-FTL-CSRF": self.csrf,
                },
                timeout=5,
            )
            if pihole_response.status_code == 204:
                logger.info(f"Deleted Pihole Domain: {domain}")
                return True

        logger.error(f"Domain {domain} not found")
        return False

    # Method for Updating Pihole
    # Decides whether Domain is to be pushed to allow or deny method
    def update_pihole_domain(self, domain, domain_type):

        self.delete_pihole_domain(domain)

        if domain_type == "allow":
            return self.add_to_allow_pihole_blocklist(domain)
        if domain_type == "deny":
            return self.add_to_block_pihole_blocklist(domain)

    # Method for checking if Domain is present on Pihole
    def check_pihole_domain(self, given_domain):

        logger.info("Checking Domain on Pihole")

        pihole_domains = self.get_cache_data(
            name="pihole_domains", method=self.__get_all_domains, duration_time=400
        )

        for domain in pihole_domains:
            if domain["domain"] == given_domain:
                return True
        return False

    # Method for checking the type of Domain on Pihole
    def __get_pihole_domain_type(self, given_domain):

        logger.info("Getting Domain Type")
        pihole_domains = self.get_cache_data(
            name="pihole_domains", method=self.__get_all_domains, duration_time=400
        )

        if pihole_domains:
            for domain in pihole_domains:
                if domain["domain"] == given_domain:
                    if domain["type"]:
                        return domain["type"]
                    return None
                return None
        return None

    #################################################

    # Method for Obtaining all of the Domains
    def __get_database_summary(self, current_time, hour_ago):

        data_json = self.__make_request(
            method="GET",
            api_destination="api/stats/database/summary",
            params={"from": str(hour_ago), "until": str(current_time)},
        )

        return data_json

    # General Pihole Information:
    # Get Pihole's Statistical Data for Later Display
    def get_pihole_summary(self, from_time: datetime, until_time: datetime):

        logger.info("Getting Pihole Database Summary")

        current_time = from_time.timestamp()

        hour_ago = until_time.timestamp()

        summary = self.get_cache_data(
            "database_summary", self.__get_database_summary, 300, current_time, hour_ago
        )

        return summary

    # Method for Getting Blocked Clients from Pihoole / Database
    def get_recent_blocked_clients(self):

        # Getting Pihole Queries
        queries = self.get_cache_data(
            name="recent_domains", method=self.__get_queries, duration_time=40
        )

        pihole_events = []

        if queries is not None:

            for query in queries:

                status = self.__classify_status(query["status"])

                if status != "block":
                    continue

                pihole_events.append(
                    {
                        "time": query["time"],
                        "domain": query["domain"],
                        "source": "Pihole",
                    }
                )

        # Getting Domains from Database
        from_time = (datetime.now(timezone.utc) - timedelta(hours=24)).timestamp()
        until_time = datetime.now(timezone.utc).timestamp()
        recent_db_domains = self.database.get_db_recent_domains(from_time, until_time)

        if recent_db_domains is None and queries is not None:
            pihole_events.sort(reverse=True, key=lambda event: event["time"])
            return pihole_events[:5]

        if recent_db_domains is None and queries is None:
            logger.warning("No domains obtained from Pihole and database.")
            return None

        ml_events = []

        if recent_db_domains is not None:
            for domain in recent_db_domains:
                ml_events.append(
                    {
                        "time": domain.date_created.timestamp(),
                        "domain": domain.domain_name,
                        "source": "BlockWay ML",
                    }
                )

        events = pihole_events + ml_events
        events.sort(reverse=True, key=lambda event: event["time"])

        logger.info(f"Pi-hole events: {pihole_events}")
        logger.info(f"ML events: {ml_events}")
        logger.info(f"Combined events: {events[:5]}")

        return events[:5]
