import requests
from dotenv import load_dotenv
import os

# Load .env variables into os environment
load_dotenv()
pi_ip = '192.168.9.108'

PIHOLE_AUTH_URL = f'http://{pi_ip}:8080/api/auth/'
PIHOLE_QUERY_URL = f'http://{pi_ip}:8080/api/queries'
PIHOLE_STATS_URL = f'http://{pi_ip}:8080/api/stats/recent_blocked'

password = os.getenv("TEST_API")

def test_can_get_endpoint():

    print('#################################################')
    print('Sending Request')
    print(f'To AUTH URL: {PIHOLE_AUTH_URL}')
    print(f'Password: {password}')

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

    print('#################################################')
    print('Sending Request')
    print(f'To: {PIHOLE_QUERY_URL}')


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
    


def test_getting_blocked_queries():
    print('#################################################')
    print('Sending Request to Recent Blocked')
    print(f'To: {PIHOLE_STATS_URL}')


    sid, csrf = test_can_get_endpoint()

    print(f'SID in receiving queries test {sid}')
    response = requests.get(
        PIHOLE_STATS_URL,
        headers={
            "X-FTL-SID": sid,
            "X-FTL-CSRF": csrf
            },
        timeout = 5
)

    assert response.status_code == 200

    response_data = response.json()

    blocked = response_data['blocked']

    print(blocked)