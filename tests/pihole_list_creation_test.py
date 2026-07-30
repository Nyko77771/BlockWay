"""
Adding to Pihole Tests
"""
import requests
import pytest

password = "@connection5"
pihole_url = "http://192.168.9.108:8080"
sid = None
csrf = None

# Domainn to Add
DOMAIN_TO_ADD = "Some_Domain_I_Made_Up.com"

def get_auth():
    pihole_response = requests.post(
        f"{pihole_url}/api/auth",
        json={"password": password},
        timeout=5,
    )

    data_json = pihole_response.json()

    print(f"Response: {pihole_response.status_code}")

    if "session" not in data_json:
        print(f"Pihole authentication failed")
        raise RuntimeError("Pihole authentication failed")

    status_code = pihole_response.status_code

    print(f"Status: {status_code} - Data Obtained")

    sid = data_json["session"]["sid"]

    csrf = data_json["session"]["csrf"]

    print(f"SID obtained: {sid}")
    print(f"CSRF obtained: {csrf}")

    return sid, csrf
"""
def test_add_to_pihole():

    sid, csrf = get_auth()

    pihole_response = requests.post(
        f"{pihole_url}/api/domains/deny/exact",
        headers={
            "X-FTL-SID": sid,
            "X-FTL-CSRF": csrf,
        }, # type: ignore
        json={
            "domain": DOMAIN_TO_ADD,
        },
        timeout=5,
    )

    assert pihole_response.status_code == 201
"""
"""
def test_update_pihole_domain():

    sid, csrf = get_auth()

    pihole_response = requests.put(
            f"{pihole_url}/api/domains/allow/exact/{DOMAIN_TO_ADD}",
            headers={
               "X-FTL-SID": sid, "X-FTL-CSRF": csrf 
            },
            json={
                "type": "deny",
                "kind": "exact",
                "oldtype": "allow"
            },
            timeout=5,
        )
    pihole_domains = pihole_response.json()
    print("Returned Information: ", pihole_domains)
    print("Returned Status: ", pihole_response.status_code)
    assert str(pihole_domains["type"]) == "allow"
"""

def test_delete_pihole_domain():

    sid, csrf = get_auth()
    
    pihole_response = requests.delete(
        f"{pihole_url}/api/domains/allow/exact/{DOMAIN_TO_ADD}",
        headers={
            "X-FTL-SID": sid,
            "X-FTL-CSRF": csrf,
        }, # type: ignore
        timeout=5,
    )

    assert pihole_response.status_code == 204
