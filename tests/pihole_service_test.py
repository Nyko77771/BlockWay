import requests
from dotenv import load_dotenv
import os
from block_app.services.pihole_service import Pihole
from datetime import datetime, timedelta


# Load .env variables into os environment
load_dotenv()

queries = {
    "queries": [
        {
            "id": 5994,
            "time": 1782992388.0363295,
            "type": "A",
            "status": "CACHE",
            "dnssec": "SECURE",
            "domain": "vpn-api.proton.me",
            "upstream": null,
            "reply": {
                "type": "IP",
                "time": 1.9550323486328125e-05
            },
            "client": {
                "ip": "192.168.9.105",
                "name": null
            },
            "list_id": null,
            "ede": {
                "code": -1,
                "text": null
            },
            "cname": null
        },
        {
            "id": 5993,
            "time": 1782992209.549947,
            "type": "PTR",
            "status": "CACHE",
            "dnssec": "INSECURE",
            "domain": "105.9.168.192.in-addr.arpa",
            "upstream": null,
            "reply": {
                "type": "NXDOMAIN",
                "time": 0.00011539459228515625
            },
            "client": {
                "ip": "127.0.0.1",
                "name": "localhost"
            },
            "list_id": null,
            "ede": {
                "code": -1,
                "text": null
            },
            "cname": null
        },
    ]                                     
}


pi_ip = '192.168.9.109'

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

"""

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

"""

def test_recent_time():

    recent_time = datetime.now().timestamp()

    time_difference = (datetime.now() - timedelta(hours=1)).timestamp()

    assert recent_time > time_difference


def test_timestamp():

    timestamp = 1782893000

    date_time = datetime.fromtimestamp(timestamp)

    assert date_time.year == 2026




"""
# Testing Pihole Class

pi_ip = '192.168.9.108'
password = os.getenv("TEST_API")

pihole = Pihole(pi_ip, password)

pihole
"""