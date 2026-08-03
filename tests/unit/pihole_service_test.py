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
            "upstream": None,
            "reply": {"type": "IP", "time": 1.9550323486328125e-05},
            "client": {"ip": "192.168.9.105", "name": None},
            "list_id": None,
            "ede": {"code": -1, "text": None},
            "cname": None,
        },
        {
            "id": 5993,
            "time": 1782992209.549947,
            "type": "PTR",
            "status": "CACHE",
            "dnssec": "INSECURE",
            "domain": "105.9.168.192.in-addr.arpa",
            "upstream": None,
            "reply": {"type": "NXDOMAIN", "time": 0.00011539459228515625},
            "client": {"ip": "127.0.0.1", "name": "localhost"},
            "list_id": None,
            "ede": {"code": -1, "text": None},
            "cname": None,
        },
    ]
}


pi_ip = "192.168.9.109"

PIHOLE_AUTH_URL = f"http://{pi_ip}:8080/api/auth/"
PIHOLE_QUERY_URL = f"http://{pi_ip}:8080/api/queries"
PIHOLE_STATS_URL = f"http://{pi_ip}:8080/api/stats/recent_blocked"
PIHOLE_SUMMARY_URL = f"http://{pi_ip}:8080/api/stats/database/summary"
PIHOLE_TOP_CLIENTS_URL = f"http://{pi_ip}:8080/api/stats/database/top_clients"


password = os.getenv("PASSWORD")


# Testing API Connections
def __get_endpoint():

    print("#################################################")
    print("Sending Request")

    response = requests.post(
        PIHOLE_AUTH_URL, json={"password": str(password)}, timeout=5
    )

    response_data = response.json()

    print(response_data)

    sid = response_data["session"]["sid"]
    csrf = response_data["session"]["csrf"]

    print(f"SID obtained: {sid}")
    print(f"CSRF obtained: {csrf}")

    return sid, csrf


def __get_summary():

    sid, csrf = __get_endpoint()

    current_time = datetime.now().timestamp()

    hour_ago = (datetime.now() - timedelta(hours=1)).timestamp()

    pihole_response = requests.get(
        PIHOLE_SUMMARY_URL,
        headers={"X-FTL-SID": sid, "X-FTL-CSRF": csrf},
        params={"from": str(hour_ago), "until": str(current_time)},
        timeout=5,
    )

    summary = pihole_response.json()

    print(summary)

    assert "sum_queries" in summary
    assert "sum_blocked" in summary


def test_get_top_client():

    sid, csrf = __get_endpoint()

    current_time = datetime.now().timestamp()

    hour_ago = (datetime.now() - timedelta(hours=1)).timestamp()

    pihole_response = requests.get(
        PIHOLE_TOP_CLIENTS_URL,
        headers={"X-FTL-SID": sid, "X-FTL-CSRF": csrf},
        params={"from": str(hour_ago), "until": str(current_time)},
        timeout=5,
    )

    top_clients = pihole_response.json()

    print(top_clients)

    assert "clients" in top_clients
    assert "total_queries" in top_clients
    assert "blocked_queries" in top_clients


"""

def test_checking_returned_queries():
    print('#################################################')

    sid, csrf = __get_endpoint()

    print(f'SID in receiving queries test {sid}')
    response = requests.get(
        PIHOLE_QUERY_URL,
        headers={
            "X-FTL-SID": sid,
            "X-FTL-CSRF": csrf
            },
        timeout = 5
        )

    data_json = response.json()

    queries = data_json['queries']

    unique_statuses = set()

    for query in queries:
        unique_statuses.add(query['status'])

    for status in unique_statuses:
        print(f'Status Type: {status}')

    assert response.status_code == 200




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

# Testing Timestamp Methods
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

# Testing Query Returns
"""
def test_querying():
    assert len(queries['queries']) == 2

def test_split():

    domains = queries['queries']

    blocked_status = ['GRAVITY']
    allowed_status = ['FORWARDED', 'CACHE', 'CACHE_STALE']
    in_progress_status = ['IN_PROGRESS']

    blocked_domains = set()
    permited_domains = set()

    for domain in domains:

        if domain['status'] in in_progress_status:
                continue

        if  domain['status'] in blocked_status:
                blocked_domains.add(domain['domain'])
        else:
                permited_domains.add(domain['domain'])

    assert len(blocked_domains) == 0
    assert len(permited_domains) == 2
"""
