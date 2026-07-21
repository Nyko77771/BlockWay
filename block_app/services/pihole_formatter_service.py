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
            path = sections.path
            query = sections.query
            fragment = sections.fragment

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
            if path:
                return False
            if query:
                return False
            if fragment:
                return False
            else:
                return True

        except Exception:
            return False



