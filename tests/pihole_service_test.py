import requests
from dotenv import load_dotenv
import os

# Load .env variables into os environment
load_dotenv()

PIHOLE_AUTH_URL = 'http://localhost:8080/api/auth/'
PIHOLE_QUERY_URL = 'http://localhost:8080/api/queries'
password = os.getenv("TEST_API")

def test_can_get_endpoint():
    response = requests.post(
    PIHOLE_AUTH_URL,
    json={"password": password},
    timeout = 5
)

    assert response.status_code == 200

    response_data  = response.json()

    print(response_data)

    sid = response_data['session']['sid']
    csrf = response_data['session']['csrf']

    print(f'SID obtained: {sid}')
    print(f'CSRF obtained: {csrf}')

    return sid, csrf


def test_receiving_queries():

    sid, csrf = test_can_get_endpoint()

    print(f'SID in receiving queries test {sid}')
    response = requests.get(
        PIHOLE_QUERY_URL,
        headers={
            "X-FTL-SID": sid,
            "X-FTL-CSRF": csrf
            },
        timeout = 5
)

    assert response.status_code == 200

    response_data = response.json()

    print(response_data)
