from datetime import datetime, timezone, timedelta
from tests.conftest import pihole_url
from block_app.services.pihole_service import Pihole

until_time = datetime.now(timezone.utc)
from_time = (datetime.now(timezone.utc) - timedelta(hours=24)).timestamp()

# Checking Authentication with Pihole
def test_pihole_sid(pihole_url):
    pihole = Pihole(pihole_url)
    pihole.authenticate()

    assert pihole.sid is not None
    assert pihole.csrf is not None

# Checking Pihole Summary Retrieval
def test_pihole_summary(pihole_url, until_time, from_time):
     pihole = Pihole(pihole_url)

     pihole_summary = pihole.get_pihole_summary(from_time=from_time, until_time=until_time)

     assert pihole_summary is not None

# Checking if Pihole adds to malicious domains
def test_pihole_malicious_block(pihole_url):
    pihole = Pihole(pihole_url)

    bad_domain = "bad_domain.com"

    result = pihole.add_to_block_pihole_blocklist(bad_domain)

    assert result is True

# Checking if Pihole adds to benign domains
def test_pihole_benign_allow(pihole_url):
    pihole = Pihole(pihole_url)

    good_domain = "good_domain.com"

    result = pihole.add_to_allow_pihole_blocklist(good_domain)

    assert result is True#

# Checking if Pihole updates benign to malicious domain
def test_pihole_benign_to_malicious(pihole_url):
    pihole = Pihole(pihole_url)

    update_domain = "good_domain.com"

    result = pihole.update_pihole_domain(domain=update_domain, domain_type='deny')

    assert result is True

# Checking if Pihole update fails with incorrect type
def test_pihole_benign_to_malicious_fail(pihole_url):
    pihole = Pihole(pihole_url)

    update_domain = "good_domain.com"

    result = pihole.update_pihole_domain(domain=update_domain, domain_type='other')

    assert result is False