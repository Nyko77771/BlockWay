# Importin os library to traverse file locations
import os
# Importing platform library to get information about platform
import platform
# Importing time module
import time
# Importing psutil utility
import psutil
#  Importing datetime
from datetime import datetime, timezone, timedelta, tzinfo
# Importing Custom Services
from block_app.services.log_service import logger
from block_app.services.pihole_service import Pihole
from block_app.services.run_ml_start_service import is_running


class DashboardService:

    def __init__(self, address=None):
        self.pihole = Pihole(address)

    ### --- NORMAL OVERVIEW FUNCTIONS --- ###
    def get_table_data(self, time_conversion=False):
        if self.pihole.contains_address():
            recent_blocked_clients = self.pihole.get_recent_blocked_clients()

            if time_conversion:
                return self.__convert_time(recent_blocked_clients)
            return recent_blocked_clients
        else:
            return None

    def get_blocked_allowed_totals(self):
        domains = self.__get_blocked_allowed()
        blocked = 0
        allowed = 0
        if domains is not None:
            for domain in domains:
                status = self.pihole.get_status(domain["status"])

                if status == "block":
                    blocked += 1
                elif status == "allow":
                    allowed += 1

        logger.info(f"Blocked: {blocked}, Allowed: {allowed}")

        return {
            "allowed": allowed,
            "blocked": blocked
        }

    def get_last_24_hours(self):

        recent_blocked_queries = self.get_table_data()

        if recent_blocked_queries is None:
            return {
                "labels": [],
                "values": []
            }

        hourly_queries = [0] * 24
        queries = {}

        for query in recent_blocked_queries:

            logger.info(f"Time {query["time"]} ; Type : {type(query["time"])}")

            if isinstance(query["time"], float) or isinstance(query["time"], int):
                time_format = datetime.fromtimestamp(query["time"])
            elif isinstance(query["time"], str):
                time_format = datetime.fromisoformat(query["time"])
            elif isinstance(query["time"], datetime):
                time_format = query["time"]
            else:
                logger.warning("Unknown Time Format")
                continue

            hour = time_format.hour

            hourly_queries[hour] += 1

        labels = [
            f"{hour:02d}:00"
            for hour in range(24)
        ]

        queries = {
                "labels": labels,
                "values": hourly_queries

            }

        i=1
        for query in queries:
            logger.info(f'Query {i}: {query}')
            i += 1

        return queries

    def get_stats(self):

        until_time = datetime.now(timezone.utc)
        from_time = until_time - timedelta(hours=24)

        pi_totals = 0
        ml_totals = 0
        ml_blocked = 0
        threat_total = 0
        activity = "Active"

        db_queries = self.pihole.database.get_db_domains()

        logger.info(f"DB Domains found: {db_queries}")

        pihole_queries = self.pihole.get_pihole_summary(from_time, until_time)

        logger.info(f"Pihole Domains found: {pihole_queries}")


        if db_queries:
            for query in db_queries:
                query_created = query.date_created
                query_with_utc = self.__get_timezone(query_created) # type: ignore

                print(query_created, query_created.tzinfo)
                print(from_time, from_time.tzinfo)

                if query_with_utc >= from_time: # type: ignore
                    ml_totals += 1
                    if query.blocked_domain: # type: ignore
                        ml_blocked += 1


        if pihole_queries is not None:
            pi_totals = pihole_queries["sum_queries"]
            blocked_number = str(pihole_queries["sum_blocked"])
            if blocked_number is not None and blocked_number.isdigit():
                threat_total = int(blocked_number) + ml_blocked
            else:
                threat_total = ml_blocked

        stats = {
            "pi_query": pi_totals,
            "ml_query": ml_totals,
            "total_threats": threat_total,
            "activity": activity,
        }

        return stats

    # Method for Adding Timezone to DB Resuls:
    def __get_timezone(self, passed_datetime: datetime | None) -> datetime | None:
        if passed_datetime is None:
            return None
        if passed_datetime.tzinfo is None:
            return passed_datetime.replace(tzinfo=timezone.utc)
        return passed_datetime


    # Method for Getting Recently Blocked Domains
    def __get_blocked_allowed(self):
         if self.pihole.contains_address():
             return self.pihole.get_recent_pihole_domains()
         return None

    # Method for Converting UNIX Timestamp to Datetime (H:M:S)
    def __convert_time(self, queries_list):

        appended_queries = []

        for query in queries_list:

            try:
                query_time =  query['time']

                if isinstance(query_time, float) or isinstance(query["time"], int):
                    format_time = datetime.fromtimestamp(query["time"]).strftime("%H:%M:%S")
                elif isinstance(query_time, str):
                    format_time = datetime.fromisoformat(query["time"]).strftime("%H:%M:%S")
                else:
                    format_time = "Unknown"

            except ValueError:
                format_time = "Unknown"

            appended_queries.append(
                {
                    "time": format_time,
                    "domain": query["domain"],
                    "source": query["source"]
                }
            )

            return appended_queries

    ### --- THREAT FUNCTIONS --- ###
    def get_threat_stats(self):#

        db_stats = self.pihole.database.get_threat_stats()

        total_threats = 0
        ml_blocks = 0
        allowed = 0
        average_confidence_score = 0

        if db_stats:
            total_threats = db_stats["total_threats"]
            ml_blocks = db_stats["ml_blocks"]
            allowed = db_stats["allowed"]
            average_confidence_score = db_stats["average_confidence_score"]

        return {
            "total_threats": total_threats,
            "ml_blocks": ml_blocks,
            "allowed": allowed,
            "average_confidence_score": average_confidence_score
        }

    ### --- SYSTEM INFO FUNCTIONS --- ###
    def get_system_information(self):

        logger.info("Getting System Information")

        db_size = ""

        # Getting Pihole Status
        pihole = self.pihole.connectionn_checker.is_connected()

        # Getting ML Information
        ml = self.__check_ml_status()

        # Getting Version
        version =self.__get_current_system_version()

        # Getting System's Python Version
        python = platform.python_version()

        # Getting os Version
        os = platform.system()

        # Getting Uptime Information
        uptime = self.__get_uptime()

        # Getting CPU Information
        cpu = psutil.cpu_percent()

        # Getting Memory Informatio
        used_memory = psutil.virtual_memory().percent
        available_memory = 100 - used_memory
        round_available_memory = round(available_memory, 1)

        # Getting Total Domains
        total_domains = self.__get_domain_totals()

        # Getting db size
        db_size = self.__get_db_size()


        system_information = {
            "pihole": pihole,
            "ml": ml,
            "version": version,
            "python": python,
            "os": os,
            "uptime": uptime,
            "cpu": cpu,
            "used_memory": used_memory,
            "available_memory": round_available_memory,
            "total_domains": total_domains,
            "db_size": db_size 
        }

        return system_information

    # Method for Getting DB file size
    def __get_db_size(self):
        path = "block_app/database/block_way.db"
        if os.path.exists(path):
            db_size = os.path.getsize(path)
            size_in_mb = db_size / (1024 * 1024)
            rounded_size = round(size_in_mb, 2)
            return f"{rounded_size}mb"
        return 'Unknown'

    # Method for Countig total of Processed Domains
    def __get_domain_totals(self):
        try:
            logger.info("Counting Total of Domains on Database")
            count = self.pihole.database.get_domains_count()
            return count
        except Exception:
            return 0

    # Methodfor Getting Uptime of System
    def __get_uptime(self):
        logger.info("Getting Uptime Details")
        seconds = int(time.time() - psutil.boot_time())

        days, days_remainder = divmod(seconds, 86400) # minutes * hour * day = 86400
        hours, hours_remainder = divmod(days_remainder, 3600) # minutes * hour = 3600
        minutes, minutes_remainder = divmod(hours_remainder, 60) # hour (60)
        return f"{days}Day {hours}Hours {minutes}Minutes"


    # Method for checking ML Service Status
    def __check_ml_status(self):
        if is_running:
            return 'Active'
        else:
            return "Offline"

    # Method for Getting the Version of the BlockWay
    def __get_current_system_version(self):
        return "BlockWay v1"