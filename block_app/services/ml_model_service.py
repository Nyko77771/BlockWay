from joblib import load
import pandas as pd
import re
import tldextract as tld
import Levenshtein

class DomainAnalyses:

    popular_domain_data_frame = None

    def __init__(self):
        self.logistic_model = load('models/logistic.pkl')
        self.random_forrest = load('models/r_forrest.pkl')
        print('Models Loaded')

    # TO DO
    def create_x_features(self, url):
        return [
            self._make_length(url),
            self._make_has_ip(url),
            self._make_digit_count(url),
            self.__make_dot_count(url),
            self.__make_has_subdomain(url),
            self.__make_subdomain_count(url),
            self.__make_hyphen_count(url),
            self.__make_special_count(url),
            self.__make_host_in_subdomain(url),
            self.__make_host_in_domain(url),
            self.__make_similarity(url),
            self.__make_has_com(url),
            self.__make_has_org(url),
            self.__make_has_country_code(url)
        ]

    def __prediction(self, model, url):
        x_test = self.create_x_features(url)
        prediction = model.predict(x_test)
        return prediction[0]

    def logistic_prediction(self, url):
        prediction_score = self.__prediction(self.logistic_model, url)
        return prediction_score

    def random_forrest_prediction(self, url):
        prediction_score = self.__prediction(self.random_forrest, url)
        return prediction_score

    # ADD PRIVATE METHODS
    # WILL BE USED FOR CREATING FEATURES

    ####################################
    # Need Features:
    # 0. Domain - (To DROP before conversion)

    # 1. Length -
    # 2. Has_IP -
    # 3. Digit_Count -
    # 4. Dot_Count -
    # 5. Has_Subdomain -
    # 6. Subdomain_Count -
    # 7. Hyphen_Count -
    # 8. Special_Count -
    # 9. Host_in_Subdomain -
    # 10. Host_in_Domain -
    # 11. Similarity -
    # 12. Has .com -
    # 13. Has .org -
    # 14. Has country code

    # Private Class Methods

    # Method for uploading popular domains csv
    def __get_popular_domains(self):
        self.popular_domain_data_frame = pd.read_csv('models/popular_domains.csv')
        return

    # Method For Checking if Domain was given
    def _check_domain(self, url):
        sections = tld.extract(url)
        domain = sections.domain
        subdomain = sections.subdomain
        suffix = sections.suffix

        regex = '^(?:[a-zA-Z0-9]+\.)+[a-zA-Z]{2,}$'
        domain_pattern = re.compile(regex)
        if domain != None and subdomain != None and suffix != None and domain_pattern.fullmatch(url):
            return True
        return False

    def _make_length(self, url):
        length = len(url)
        return length

    def _make_has_ip(self, url):
        pattern = r'(\d{1,3}\.){3}\d{1,3}'
        ip_patter_object = re.compile(pattern)
        matched_object = ip_patter_object.search(url)
        ip_num = matched_object.group()
        return 1 if ip_num else 0

    def _make_digit_count(self, url):
        count = 0
        for c in url:
            if c.isdigit():
                count += 1
        return count

    def __make_dot_count(self, url):
        return url.count('.')

    def __make_has_subdomain(self, url):
        sections = tld.extract(url)
        return bool(sections.subdomain)

    def __make_subdomain_count(self, url):
        sections = tld.extract(url)
        subdomain = sections.subdomain
        if subdomain:
            return len(subdomain.split('.'))
        else:
            return 0

    def __make_hyphen_count(self, url):
        return url.count('-')

    def __make_special_count(self, url):
        count = 0
        for c in url:
            if not c.isalnum():
                count += 1
        return count

    def __make_host_in_subdomain(self, url):
        if self.popular_domain_data_frame is None:
            self.__get_popular_domains()
        sections = tld.extract(url)
        hostname = sections.domain.lower()
        subdomain = sections.subdomain.lower()
        for domain in self.popular_domain_data_frame:
            domain_name = domain.split('.')[0]
            if domain_name in subdomain and hostname != domain_name:
                return 1
        return 0

    def __make_host_in_domain(self, url):
        if self.popular_domain_data_frame is None:
            self.__get_popular_domains()
        sections = tld.extract(url)
        hostname = sections.domain.lower()
        if hostname in self.popular_domain_data_frame['Domain']:
            return 1
        return 0

    def __make_similarity(self, url):
        try:
            if self.popular_domain_data_frame is None:
                self.__get_popular_domains()
            sections = tld.extract(url)
            hostname = sections.domain.lower()
            best_score = 0
            for domain in self.popular_domain_data_frame['Domain']:
                similiraty_score = Levenshtein.ratio(domain, hostname)
                if similiraty_score > best_score:
                    return similiraty_score
                else:
                    return best_score
        except Exception as e:
            print('')


    def __make_has_com(self, url):
        sections = tld.extract(url)
        suffix = sections.suffix
        return int(suffix.lower() == 'com')

    def __make_has_org(self, url):
        sections = tld.extract(url)
        suffix = sections.suffix
        return int(suffix.lower() == 'org')

    def __make_has_country_code(self, url):
        sections = tld.extract(url)
        suffix = sections.suffix
        last_section = suffix.split('.')[-1]
        return int(len(last_section) == 2)







