# Getting time module for getting current time
import time

# Getting request module for establishing api connections
import requests

# Getting custom logger module
from block_app.services.log_service import logger


class PiholeConnectionChecker:
    def __init__(self, pihole):
        logger.info("Initialing Pihole Connection Checker")
        self.pihole = pihole
        self.previous_result = False
        self.previous_check = 0
        self.cache = 30

    def is_connected(self):
        current_time = time.time()

        if (current_time - self.previous_check) > self.cache:
            result = self.__check_connection()
            self.previous_result = result
            self.previous_check = current_time

        return self.previous_result

    def __check_connection(self):
        try:
            logger.info("Checking Connection to Pihole")
            pihole_address = self.pihole.get_address()
            logger.info(f"Checking Pihole URL: {pihole_address}")
            response = requests.get(
                str(pihole_address).rstrip("/") + "/admin/", timeout=5
            )
            logger.info(response.status_code)
            logger.info(response.headers)
            if response.ok:
                return True
            logger.warning(f"Pihole Address returned code: {response.status_code}")
            return False
        except requests.exceptions.Timeout:
            logger.exception("Connection Timed Out")
            return False
        except requests.exceptions.ConnectionError:
            logger.exception("Unable to Establish Connection to Pihole")
            return False
        except Exception:
            logger.exception("Failed to Connect to Pihole")
            return False
