from joblib import load
from block_app.services.log_service import logger

import pandas as pd
import re
import tldextract as tld
import Levenshtein
import zipfile


class DomainAnalyses:

    popular_domain_data_frame = None

    def __init__(self):
        try:
            self.random_forrest = self.__open_zip()
            self.logistic_model = load("block_app/models/logistic.pkl")
            self.scaler = load("block_app/models/scaler.pkl")
            logger.info("Models Loaded")
        except Exception as e:
            logger.exception("Exception Occurred while Loading Models")
            logger.exception(f"Exception: {e}")

    # Extracting Model from Zip File
    def __open_zip(self):
        path = "block_app/models/r_forrest.zip"

        with zipfile.ZipFile(path, "r") as zObject:

            with zObject.open("r_forrest.pkl") as file:
                model = load(file)
        return model

    # Method for creating analysis features
    def create_x_features(self, url):

        # First checking if domain is in correct format
        if not self._check_domain(url):
            logger.exception(f'Domain {url} is invalid')
            raise ValueError

        features = pd.DataFrame([{
            "Length": self._make_length(url),
            "Has_IP": self._make_has_ip(url),
            "Digit_Count": self._make_digit_count(url),
            "Dot_Count":  self.__make_dot_count(url),
            "Has_Subdomain": self.__make_has_subdomain(url),
            "Subdomain_Count": self.__make_subdomain_count(url),
            "Hyphen_Count": self.__make_hyphen_count(url),
            "Special_Count": self.__make_special_count(url),
            "Host_in_Subdomain": self.__make_host_in_subdomain(url),
            "Host_in_Domain": self.__make_host_in_domain(url),
            "Similarity": self.__make_similarity(url),
            "Has_com": self.__make_has_com(url),
            "Has_org": self.__make_has_org(url),
            "Has_Country_Code": self.__make_has_country_code(url),
            }])
        return features

    def __prediction(self, model, url, logistic=False):
        x_test = self.create_x_features(url)
        prediction = []
        if logistic:
            x_scaled = self.scaler.transform(x_test)
            prediction = model.predict(x_scaled)
        else:
            prediction = model.predict(x_test)
        return prediction[0]

    def __probability(self, model, url, logistic=False):
        x_test = self.create_x_features(url)
        probability = []
        if logistic:
            x_scaled = self.scaler.transform(x_test)
            probability = model.predict_proba(x_scaled)
        else:
            probability = model.predict_proba(x_test)
        return probability[0][1]

    def logistic_probability(self, url):
        probability_score = self.__probability(self.logistic_model, url, True)
        return probability_score

    def logistic_prediction(self, url):
        logger.info("Performing Logistic Prediction")
        prediction_score = self.__prediction(self.logistic_model, url, True)
        logger.info(f"Logistic prediction Score: {prediction_score}")
        return prediction_score

    def random_forrest_prediction(self, url):
        logger.info("Performing Random Forrest Prediction")
        prediction_score = self.__prediction(self.random_forrest, url)
        logger.info(f"Random Forrest prediction Score: {prediction_score}")
        return prediction_score

    ####################################

    # Private Class Methods

    # Method for uploading popular domains csv
    def __get_popular_domains(self):
        self.popular_domain_data_frame = pd.read_csv("block_app/models/popular_domains.csv")
        return

    # Method For Checking if Domain was given
    def _check_domain(self, url):
        try:
            sections = tld.extract(url)
            sections = tld.extract(url) 
            domain = sections.domain
            subdomain = sections.subdomain 
            suffix = sections.suffix

            if (
                domain
                and subdomain and suffix
            ):
                regex = r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"

                return bool(
                    re.fullmatch(regex, url)
                )

        except Exception:
            logger.exception(f"Domain validation failed {url}")
        return False

    def _make_length(self, url):
        length = len(url)
        return length

    def _make_has_ip(self, url):
        pattern = r"(\d{1,3}\.){3}\d{1,3}"
        ip_patter_object = re.compile(pattern)
        matched_object = ip_patter_object.search(url)
        if matched_object is None:
            return 0
        ip_num = matched_object.group()
        return 1 if ip_num else 0

    def _make_digit_count(self, url):
        count = 0
        for c in url:
            if c.isdigit():
                count += 1
        return count

    def __make_dot_count(self, url):
        return url.count(".")

    def __make_has_subdomain(self, url):
        sections = tld.extract(url)
        return int(bool(sections.subdomain))

    def __make_subdomain_count(self, url):
        sections = tld.extract(url)
        subdomain = sections.subdomain
        if subdomain:
            return len(subdomain.split("."))
        else:
            return 0

    def __make_hyphen_count(self, url):
        return url.count("-")

    def __make_special_count(self, url):
        count = 0
        for c in url:
            if not c.isalnum():
                count += 1
        return count

    def __make_host_in_subdomain(self, url):
        if self.popular_domain_data_frame is None:
            self.__get_popular_domains()
        popular_domains = self.popular_domain_data_frame
        if popular_domains is None:
            return 0
        sections = tld.extract(url)
        hostname = sections.domain.lower()
        subdomain = sections.subdomain.lower()
        for domain in popular_domains:
            domain_name = str(domain).split(".")[0]
            if domain_name in subdomain and hostname != domain_name:
                return 1
        return 0

    def __make_host_in_domain(self, url):
        if self.popular_domain_data_frame is None:
            self.__get_popular_domains()
        popular_domains = self.popular_domain_data_frame
        if popular_domains is None:
            return 0
        sections = tld.extract(url)
        hostname = sections.domain.lower()
        if hostname in popular_domains["Domain"]:
            return 1
        return 0

    def __make_similarity(self, url):
        if self.popular_domain_data_frame is None:
            self.__get_popular_domains()

        sections = tld.extract(url)
        hostname = sections.domain.lower()
        best_score = 0
        for domain in self.popular_domain_data_frame["Domain"]: # type: ignore
            similiraty_score = Levenshtein.ratio(domain, hostname)
            if similiraty_score > best_score:
                return similiraty_score
            else:
                return best_score

    def __make_has_com(self, url):
        sections = tld.extract(url)
        suffix = sections.suffix
        return int(suffix.lower() == "com")

    def __make_has_org(self, url):
        sections = tld.extract(url)
        suffix = sections.suffix
        return int(suffix.lower() == "org")

    def __make_has_country_code(self, url):
        sections = tld.extract(url)
        suffix = sections.suffix
        last_section = suffix.split(".")[-1]
        return int(len(last_section) == 2)
