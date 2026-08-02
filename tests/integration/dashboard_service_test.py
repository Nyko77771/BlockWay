from block_app.services.dashboard_service import DashboardService
from block_app.services.pihole_service import Pihole

# Testing if dashboard returns table data
def test_dashboard_gets_pihole_table_data():

    pihole = Pihole()

    dash_service = DashboardService(pihole)

    table_data = dash_service.get_table_data

    assert table_data is not None

# Testing if dashboard getting data
def test_dashboard_gets_pihole_stats_data():

    pihole = Pihole()

    dash_service = DashboardService(pihole)

    stats = dash_service.get_stats()

    assert stats is not None

# Testing if dashboard getting data
def test_dashboard_gets_pihole_blocked_allowed():

    pihole = Pihole()

    dash_service = DashboardService(pihole)

    result = dash_service.get_stats()

    assert result is not None
    assert "blocked" in result
    assert "allowed" in result

# Testing to see if dashboard has more than one allowed domain
def test_dashboard_gets_pihole_allowed_total():

    pihole = Pihole()

    dash_service = DashboardService(pihole)

    result = dash_service.get_stats()

    assert result['allowed'] > 1

# Testing the last 24 hour statistics
def test_get_last_24():
    pihole = Pihole()

    dash_service = DashboardService(pihole)

    result = dash_service.get_last_24_hours()

    assert result is not None
    assert "labels" in result
    assert "values" in result

# Test to see if threat stats are returned
def test_threat_stats():
    pihole = Pihole()

    dash_service = DashboardService(pihole)

    result = dash_service.get_threat_stats()

    assert "total_threats" in result
    assert "ml_blocks" in result
    assert "allowed" in result
    assert "average_confidence_score" in result


