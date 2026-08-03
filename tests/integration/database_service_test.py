from tests.conftest import db_session
from block_app.models import db_models


# Testing Database Domain Addition
def test_add_domain(db_session):

    made_up_domain = "malicious_domain.com"

    new_domain = db_models.AnalysedDomains(
        domain_name=made_up_domain,
        prediction_type="malicious",
        prediction_score=0.95,
        blocked_domain=True,
    )

    db_session.add(new_domain)
    db_session.commit()

    saved_domain = (
        db_session.query(db_models.AnalysedDomains)
        .filter(db_models.AnalysedDomains.domain_name == made_up_domain)
        .first()
    )

    print(f"Retrieved Saved Domain: {saved_domain}")

    assert saved_domain is not None
    assert saved_domain.domain_name == made_up_domain
    assert saved_domain.blocked_domain is True


# Testing Database Domain Update
def test_update_domain(db_session):

    changed_name = "another_name.com"

    new_domain = db_models.AnalysedDomains(
        domain_name="good_domain.com",
        prediction_type="benign",
        prediction_score=0.25,
        blocked_domain=False,
    )

    # Adding New Domain
    db_session.add(new_domain)
    db_session.commit()

    # Retrieving Saved Domain
    saved_domain = (
        db_session.query(db_models.AnalysedDomains)
        .filter(db_models.AnalysedDomains.domain_name == "good_domain.com")
        .first()
    )

    # Changing Saved Domain
    saved_domain.domain_name = changed_name
    saved_domain.blocked_domain = True
    db_session.commit()

    # Getting Updated Domain
    updated_domain = (
        db_session.query(db_models.AnalysedDomains)
        .filter(db_models.AnalysedDomains.domain_name == changed_name)
        .first()
    )

    # Analysing Changes
    assert updated_domain.domain_name == changed_name
    assert updated_domain.blocked_domain is True


def test_delete_domain(db_session):
    domain = db_models.AnalysedDomains(
        domain_name="remove-me.com",
        prediction_type="benign",
        prediction_score=0.25,
        blocked_domain=False,
                                       )

    # Adding Domain to Database
    db_session.add(domain)
    db_session.commit()

    # Removing the Saved Domain
    db_session.delete(domain)
    db_session.commit()

    # Getting the Deleted Domain
    result = (
        db_session.query(db_models.AnalysedDomains)
        .filter(db_models.AnalysedDomains.domain_name == "remove-me.com")
        .first()
    )

    # Evaluating if Domain is Not Present
    assert result is None
