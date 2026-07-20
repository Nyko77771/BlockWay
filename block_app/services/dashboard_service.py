#  Importing datetime
from datetime import datetime
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


