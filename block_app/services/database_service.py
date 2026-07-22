# Importing Local Services
from block_app.services.log_service import logger
from block_app.database.database import SessionLocal
import block_app.models.db_models as db_models

# Importing External Libraries
from datetime import datetime
from datetime import timezone


class DomainDatabase:

    ###########################################
    # User Methods
    # Method for Getting User by Username
    def get_db_user_by_username(self, username):
        db = SessionLocal()
        try:
            logger.info("Checking user type")
            logger.info(f"User: {username}")

            db_user = (
                db.query(db_models.User)
                .filter(db_models.User.username == username)
                .first()
            )

            return db_user

        except Exception:
            logger.exception("Failed to Get User by Username")
        finally:
            logger.info("Closing Database")
            db.close()

    # Method for Getting User by ID
    def get_db_user_by_id(self, user_id):
        db = SessionLocal()
        try:
            logger.info("Checking User by ID")
            logger.info(f'User ID: {user_id}')

            db_user = (
                db.query(db_models.User)
                .filter(db_models.User.id == user_id)
                .first()
            )

            return db_user

        except Exception:
            logger.exception("Failed to Get User by ID")
        finally:
            logger.info("Closing Database")
            db.close()

    # Method for Adding User
    def add_db_user(self, username, password, salt):

        db = SessionLocal()
        try:
            logger.info("Adding User")

            new_user = db_models.User(
                username=username,
                password=password,
                salt=salt,
                role_type=db_models.UserRoleEnum.NORMAL.value,
            )

            db.add(new_user)
            db.commit()

        except Exception:
            logger.exception("Failed to Add User")
        finally:
            logger.info("Closing Database")
            db.close()

    def get_default_admin(self):
        db = SessionLocal()
        try:
            logger.info("Getting User Database Details")
            db_admin = (
                db.query(db_models.User)
                .filter(db_models.User.username == "admin")
                .first()
            )
            return db_admin
        except Exception:
            logger.exception("Failed to Get Admin")
        finally:
            logger.info("Closing Database")
            db.close()

    def update_default_admin(self, username, password, salt):
        db = SessionLocal()
        try:
            db_admin = (
                db.query(db_models.User)
                .filter(db_models.User.username == "admin")
                .first()
            )
            if db_admin is None:
                raise Exception

            db_admin.username = username
            db_admin.password = password
            db_admin.salt = salt
            db.commit()

        except Exception:
            logger.exception("Admin Update Failed")
            db.rollback()
        finally:
            logger.info("Closing Database")
            db.close()

    def update_db_user_password(self, user, password):
        pass

    def check_db_admin(self):
        pass

    def update_db_user(self):
        pass

    def make_db_admin(self):
        pass

    ##############################
    # Domain Methods
    def get_db_domains(self):
        db = SessionLocal()
        try:
            logger.info("Getting Database Domains")

            db_domains = db.query(db_models.AnalysedDomains).all()

            return db_domains

        except Exception:
            logger.exception("Failed to get Domains")
        finally:
            logger.info("Closing Database")
            db.close()

    def add_db_domain(self, domain, prediction_type, score, added_to_pihole=False):
        db = SessionLocal()
        try:
            logger.info("Adding Domains")

            new_domain = db_models.AnalysedDomains(
                domain_name=domain,
                prediction_type=(
                    db_models.DomainPredictionType.MALICIOUS.value
                    if prediction_type == "malicious"
                    else db_models.DomainPredictionType.BENIGN.value
                ),
                prediction_score=score,
                blocked_domain=prediction_type == "malicious",
                added_to_pihole=added_to_pihole,
            )

            db.add(new_domain)
            db.commit()
            db.refresh(new_domain)

            return new_domain

        except Exception:
            logger.exception("Failed to Add Domain")
            logger.info("Rolling Back Domain Addition")
            db.rollback()
        finally:
            logger.info("Closing Database")
            db.close()

    def update_db_domain(self):
        pass

    def get_db_recent_domains(self, from_time, until_time):
        db = SessionLocal()
        try:
            logger.info("Getting Specific Database Domains based on Time")

            db_domains = db.query(db_models.AnalysedDomains).all()

            difference = (from_time - until_time)

            recent_domains = []

            for db_domain in db_domains:

                if db_domain.date_created >= difference:
                    recent_domains.append(db_domain)

            return recent_domains
        except Exception:
            logger.exception('An Exception Occurred')
        finally:
            logger.info("Closing Database")
            db.close()

    def get_malicious_domains(self):
        db = SessionLocal()
        try:
            logger.info("Getting Malicious Domains")
            db_malicious = db.query(db_models.AnalysedDomains).first()

            malicious_list = []
            if db_malicious is not None:
                for domain in db_malicious:
                    if domain.blocked_domain == True:
                        malicious_list.append(domain)
                return malicious_list
            return None            
        except Exception:
            logger.exception("Failed to Get Malicious Domains")
            return None
        finally:
            logger.info("Closing Database")
            db.close()


    def get_unblocked_domains(self):
        pass

    ######################################
    # Scheduler Methods
    def get_last_scan(self):
        db = SessionLocal()
        try:
            logger.info("Getting Scan Details")

            db_schedule = db.query(db_models.ScheduleConfiguration).first()

            if db_schedule is None:
                logger.info("No schedule found")
                return None

            db_last_scan = db_schedule.last_scan

            logger.info(f"Last scan: {db_last_scan}")

            return db_last_scan

        except Exception as e:
            logger.exception("Failed to Get Last Scan Details")
            logger.exception(f"{e}")
        finally:
            logger.info("Closing Database")
            db.close()

    def update_last_scan(self, type):
        db = SessionLocal()
        try:
            schedule = db.query(db_models.ScheduleConfiguration).first()

            if schedule is None:
                logger.info("Scheduler  not Set")
                raise Exception

            schedule.last_scan = datetime.now(timezone.utc)
            schedule.next_scan = datetime.now(timezone.utc)
            schedule.last_scan_status = type

        except Exception:
            logger.exception("Failed to Update the Last Scan Details")
        finally:
            logger.info("Closing Database")
            db.close()

    ######################################
    # Pihole Methods
    def get_pihole_address(self):
        db = SessionLocal()
        try:
            logger.info("Getting address")

            db_pihole = db.query(db_models.Pihole).first()

            if db_pihole is None:
                logger.info("Scheduler  not Set")
                raise Exception

            db_pi_address = db_pihole.pihole_address

            return db_pi_address

        except Exception:
            logger.exception("Failed to Get Pihole Address")
        finally:
            logger.info("Closing Database")
            db.close()

    def add_pihole_address(self, address):
        db = SessionLocal()
        try:

            new_pi_address = db_models.Pihole(
                pihole_address=address,
            )

            db.add(new_pi_address)
            db.commit()

        except Exception:
            logger.exception("Failed to Add Pihole Address")
            logger.info("Rolling Back Address Addition")
            db.rollback()
        finally:
            logger.info("Closing Database")
            db.close()
