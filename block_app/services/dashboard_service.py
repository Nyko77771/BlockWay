# Importing Local Services
from block_app.services.pihole_service import Pihole
from block_app.services.ml_model_service import DomainAnalyses
from block_app.services.database_service import DomainDatabase
from block_app.services.log_service import logger

# Importing Python Libraries
from dotenv import load_dotenv
import os

class DashboardService:

    def __init__(self, address):
        # Loading environmental variables
        load_dotenv()

        # Obtaining Password from .env
        self.password = os.getenv('PASSWORD')
        # Initialising Pihole class
        self.pihole = Pihole(address, self.password)
        # Initialising ML Analysis class
        self.ml_analyses = DomainAnalyses()
        # Initialish Database
        self.database = DomainDatabase()


    def get_probability(self):
        # Getting SID and CSRF
        self.pihole.authenticate()

        self.permitted_domains, self.blocked_domains = self.pihole.pihole_domain_analyses()

        self.ml_analyses


