import requests
from dotenv import load_dotenv
import os

# Load .env variables into os environment
load_dotenv()

PIHOLE_URL = 'http://localhost:8080/api/auth/'
password = os.getenv("TEST_API")


def test_can_get_endpoint():
    response = requests.post(
    PIHOLE_URL,
    json={"password": password},
    timeout = 5
)

    assert response.status_code == 200
    pass