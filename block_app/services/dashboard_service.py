#  Importing datetime
from datetime import datetime, timezone, timedelta
# Importing Custom Services
from block_app.services.log_service import logger
from block_app.services.pihole_service import Pihole



class DashboardService:

    def __init__(self, address=None):
        self.pihole = Pihole(address)

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
                elif status == "allowed":
                    allowed += 1

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

        if db_queries is not None:
            for query in db_queries:
                if query['date_create'] >= from_time:
                    ml_totals += 1
                if query["blocked_domain"] == True:
                    ml_blocked += 1

        pihole_queries = self.pihole.get_pihole_summary(from_time, until_time)

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
