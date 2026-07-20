#  Importing datetime
from datetime import datetime
# Importing Custom Services
from block_app.services.database_service import DomainDatabase
from block_app.services.pihole_service import Pihole


class DashboardService:

    def __init__(self, address=None):
        self.pihole = Pihole(address)

    def get_table_data(self):
        if self.pihole.contains_address():
            recent_blocked_clients = self.pihole.get_recent_blocked_clients()

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
        queries = []

        for query in recent_blocked_queries:
            time_format = datetime.fromisoformat(query["time"])

            hour = time_format.hour

            hourly_queries[hour] += 1

        labels = [
            f"{hour:02d}:00"
            for hour in range(24)
        ]

        queries.append(
            {
                "labels": labels,
                "values": hourly_queries

            }
        )

        return queries

