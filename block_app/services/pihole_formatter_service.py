# Importing urlib library for url analysis
from urllib.parse import urlsplit

# Importing Custom Logger:
from block_app.services.log_service import logger


class PiholeFormatter:
    def check_address(self, address: str):
        try:
            logger.info("Checking Pihole Address")
            address = str(address).strip()
            for c in address:
                if c.isspace():
                    logger.warning("Pihole Address Provided Contains Whitespace")
                    return False
            sections = urlsplit(address)

            scheme = sections.scheme
            netloc = sections.netloc
            port = sections.port
            path = sections.path
            query = sections.query
            fragment = sections.fragment

            logger.info("URL Provided:")
            logger.info(f"Scheme: {scheme}")
            logger.info(f"UNetloc: {netloc}")
            logger.info(f"Port: {port}")

            if scheme not in ("http", "https"):
                return False
            if not netloc:
                return False
            if not port:
                return False
            if path not in ("", "/"):
                return False
            if query:
                return False
            if fragment:
                return False
            else:
                return True

        except Exception:
            return False
