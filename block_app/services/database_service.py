# Importing Local Services
from block_app.services.log_service import logger
from block_app.database.database import SessionLocal
import block_app.models.db_models as db_models

# Importing External Libraries
from datetime import datetime, timedelta
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
            logger.info(f"User ID: {user_id}")

            db_user = (
                db.query(db_models.User).filter(db_models.User.id == user_id).first()
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

    def check_db_admin(self, username):
        db = SessionLocal()
        try:
            logger.info("Getting User Database Details")
            db_user = (
                db.query(db_models.User)
                .filter(db_models.User.username == username)
                .first()
            )

            if db_user:
                if str(db_user.role_type) == db_models.UserRoleEnum.ADMIN.__str__:
                    return True

            return False

        except Exception:
            logger.exception("Failed to Get Admin")
        finally:
            logger.info("Closing Database")
            db.close()

    def update_db_user(self):
        pass

    def make_db_admin(self, username):
        db = SessionLocal()
        try:
            logger.info("Getting User Database Details")
            db_user = (
                db.query(db_models.User)
                .filter(db_models.User.username == username)
                .first()
            )

            if db_user:
                if str(db_user.role_type) == db_models.UserRoleEnum.ADMIN:
                    logger.info("No update neccessary")

                db_user.role_type = db_models.UserRoleEnum.ADMIN
            return False

        except Exception:
            logger.exception("Failed to Get Admin")
        finally:
            logger.info("Closing Database")
            db.close()

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
            db.close()

    # Method for Adding Domains
    def add_db_domain(
        self, domain, prediction_type, score, is_string: bool, added_to_pihole=False
    ):
        db = SessionLocal()
        try:
            logger.info("Adding Domains")

            # Checks to see if the domain already exists
            if not self.__not_existing_domain(domain, is_string):  #
                # Not - then is added
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
            # If Yes (its in database) - Then Update
            else:
                if is_string:
                    self.update_db_domain_string(
                        domain, prediction_type, score, added_to_pihole
                    )
                self.update_db_domain(domain)
        except Exception:
            logger.exception("Failed to Add Domain")
            logger.info("Rolling Back Domain Addition")
            db.rollback()
        finally:
            db.close()

    # Method for Updating Domain if a String is Given
    def update_db_domain_string(self, domain, prediction_type, score, added_to_pihole):
        db = SessionLocal()
        try:

            existing_domain = (
                db.query(db_models.AnalysedDomains)
                .filter(db_models.AnalysedDomains.domain_name == str(domain))
                .first()
            )

            if existing_domain is not None:
                existing_domain.prediction_type = prediction_type
                existing_domain.prediction_score = score
                existing_domain.blocked_domain = prediction_type == "malicious"
                existing_domain.added_to_pihole = added_to_pihole
                db.commit()
                logger.info("Domain Information Updated")
            logger.info("Domain Does not Exist")
        except Exception:
            db.rollback()
            logger.exception("Failed Updating Domain")
        finally:
            db.close()

    # Method for Updating Domain if Domain Object is Given
    def update_db_domain(self, domain):
        db = SessionLocal()
        try:

            existing_domain = (
                db.query(db_models.AnalysedDomains)
                .filter(db_models.AnalysedDomains.domain_name == domain.domain_name)
                .first()
            )

            if existing_domain is not None:
                existing_domain.prediction_type = domain.prediction_type
                existing_domain.prediction_score = domain.prediction_score
                existing_domain.blocked_domain = domain.blocked_domain
                existing_domain.added_to_pihole = domain.added_to_pihole
                db.commit()
                logger.info("Domain Information Updated")
            logger.info("Domain Does not Exist")
        except Exception:
            db.rollback()
            logger.exception("Failed Updating Domain")
        finally:
            db.close()

    # Method for Getting Recent Domains
    def get_db_recent_domains(self, from_time, until_time):
        db = SessionLocal()
        try:
            logger.info("Getting Specific Database Domains based on Time")

            db_domains = db.query(db_models.AnalysedDomains).all()

            difference = from_time - until_time

            recent_domains = []

            for db_domain in db_domains:

                if db_domain.date_created >= difference:
                    recent_domains.append(db_domain)

            return recent_domains
        except Exception:
            logger.exception("An Exception Occurred")
        finally:
            db.close()

    def get_malicious_domains(self):
        db = SessionLocal()
        try:
            logger.info("Getting Malicious Domains")
            db_malicious = db.query(db_models.AnalysedDomains).first()

            malicious_list = []
            if db_malicious is not None:
                for domain in db_malicious:
                    if domain.blocked_domain is True:
                        malicious_list.append(domain)
                return malicious_list
            return None
        except Exception:
            logger.exception("Failed to Get Malicious Domains")
            return None
        finally:
            db.close()

    def __not_existing_domain(self, domain, is_str):
        db = SessionLocal()
        try:
            if is_str:
                existing_domain = (
                    db.query(db_models.AnalysedDomains)
                    .filter(db_models.AnalysedDomains.domain_name == str(domain))
                    .first()
                )
            else:
                existing_domain = (
                    db.query(db_models.AnalysedDomains)
                    .filter(db_models.AnalysedDomains.domain_name == domain.domain_name)
                    .first()
                )

            if existing_domain:
                return True
            else:
                return False
        except Exception:
            db.rollback()
            logger.exception("Failed adding domain")
        finally:
            db.close()

    def get_threat_stats(self):
        db = SessionLocal()
        try:
            last_24_hours = datetime.now(timezone.utc) - timedelta(hours=24)
            domains_in_24 = db.query(db_models.AnalysedDomains).filter(
                db_models.AnalysedDomains.date_created >= last_24_hours
            )
            total_threats = domains_in_24.count()
            ml_blocks = domains_in_24.filter(
                db_models.AnalysedDomains.blocked_domain.is_(True)
            ).count()
            allowed_scans = domains_in_24.filter(
                db_models.AnalysedDomains.blocked_domain.is_(False)
            ).count()
            average_confidence_score = 0
            domain_scores = []
            for domain in domains_in_24:
                domain_scores.append(domain.prediction_score)
            if domain_scores:
                average_confidence_score = (
                    sum(domain_scores) / len(domain_scores)
                ) * 100
            return {
                "total_threats": total_threats,
                "ml_blocks": ml_blocks,
                "allowed": allowed_scans,
                "average_confidence_score": average_confidence_score,
            }

        except Exception:
            db.rollback()
            logger.exception("Failed Getting Domain Stats")
        finally:
            db.close()

    def get_domains_count(self):
        domains = self.get_db_domains()
        logger.info("Getting Domains Count")
        count = 0
        if domains:
            for domain in domains:
                count += 1
        return count

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
            db.close()

    def update_last_scan(self, status):
        db = SessionLocal()
        try:
            schedule = db.query(db_models.ScheduleConfiguration).first()

            logger.info("Schedule object: %s", schedule)
            if schedule is None:
                logger.warning("Scheduler Configuration not Set")
                raise Exception

            schedule.last_scan = datetime.now(timezone.utc)
            schedule.next_scan = datetime.now(timezone.utc)
            schedule.last_scan_status = status

            db.commit()

        except Exception:
            logger.exception("Failed to Update the Last Scan Details")
        finally:
            db.close()

    def create_default_schedule(self):
        db = SessionLocal()
        try:
            logger.info("Checking ML Schedule")

            existing_schedule = db.query(db_models.ScheduleConfiguration).first()

            if existing_schedule:
                logger.info("ML Schedule Already Created")
                return existing_schedule

            logger.info("Creating default ML Schedule")
            schedule = db_models.ScheduleConfiguration(
                last_scan=None,
                next_scan=datetime.now(timezone.utc),
                last_scan_status=db_models.ScanStatus.NOT_STARTED,
            )

            db.add(schedule)
            db.commit()

            return schedule
        except Exception:
            db.rollback()
            logger.exception("Failed creating ML Schedule")
        finally:
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
            db.close()

    def add_pihole_address(self, address):
        db = SessionLocal()
        try:

            self.delete_pihole_address()

            given_address = str(address).strip()

            logger.info(f"Saving Pihole address: {address}")

            new_pi_address = db_models.Pihole(
                pihole_address=given_address,
            )

            db.add(new_pi_address)
            db.commit()

        except Exception:
            logger.exception("Failed to Add Pihole Address")
            logger.info("Rolling Back Address Addition")
            db.rollback()
            raise
        finally:
            db.close()

    def update_pihole_address(self, address):
        db = SessionLocal()
        try:

            pihole_address = (
                db.query(db_models.Pihole)
                .filter(db_models.Pihole.pihole_address == address)
                .first()
            )

            if pihole_address:
                pihole_address.pihole_address = address

            db.commit()

        except Exception:
            logger.exception("Failed to Update Pihole Address")
            logger.info("Rolling Back Address Update")
            db.rollback()
        finally:
            db.close()

    def delete_pihole_address(self, given_address=None):
        db = SessionLocal()
        try:
            if given_address:
                db_pihole_address = db.query(db_models.Pihole).filter(
                    db_models.Pihole.pihole_address == given_address
                ).first()

                if db_pihole_address:
                    db.delete(db_pihole_address)
                    db.commit()
                    logger.info("Deleted Last Address")
            else:
                db_pihole_addresses = db.query(db_models.Pihole).delete()
                db.commit()
                logger.info("Deleted Addresses")

        except Exception:
            logger.exception("Failed to Update Pihole Address")
            logger.info("Rolling Back Address Update")
            db.rollback()
        finally:
            db.close()