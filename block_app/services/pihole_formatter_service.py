# Importing urlib library for url analysis
from urllib.parse import urlsplit
# Importing request to establish API connection
import requests

# Importing Custom Logger:
from block_app.services.log_service import logger

class PiholeFormatter:
    def check_address(self, address: str):
        try:
            logger.info('Checking Pihole Address')
            sections = urlsplit(address)

            scheme = sections.scheme
            netloc = sections.netloc
            port = sections.port

            logger.info('URL Provided:')
            logger.info(f'Scheme: {scheme}')
            logger.info(f'UNetloc: {netloc}')
            logger.info(f'UNetloc: {port}')



            if scheme not in ('http', 'https'):
                return False
            if not netloc:
                return False
            if not port:
                return False
            else:
                return True

        except Exception:
            return False

    def check_connection(self, address):
        try:
            logger.info('Checking Connection to Pihole')
            response = requests.get(address+str('/api/docs'), timeout=5)

            if response.ok:
                return True
            logger.warning(f'Pihole returned code: {response.status_code}')
            return False
        except requests.exceptions.Timeout:
            logger.exception('Connection Timed Out')
            return False
        except requests.exceptions.ConnectionError:
            logger.exception('Unable to Establish Connection to Pihole')
            return False

