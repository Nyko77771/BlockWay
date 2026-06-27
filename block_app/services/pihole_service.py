import requests

# Establishing an overall class for Pihole connections
class Pihole:

    pihole_address = ''
    pihole_password  = ''
    pihole_sid = None
    pihole_csrf = None

    # Creating an initialiser class
    def __init__(self, pihole_address, pihole_password):
        self.pihole_address = pihole_address
        self.pihole_password = pihole_password

    def get_sid(self):
        try:
            print('Getting SID from Pihole ')
            print('On Address:')
            print(self.pihole_address)
            pihole_response = requests.post(
                f'http://{self.pihole_address}/api/auth',
                json={"password": self.pihole_password},
                timeout = 5
            )

            data_json = pihole_response.json()

            status_code = pihole_response.status_code

            print(f'Status: {status_code} - Data Obtained')

            print(f'Data obtained: {data_json}')

            self.pihole_sid = data_json["session"]["sid"]

            self.pihole_csrf = data_json["session"]["csrf"]

        except Exception as e:
            print('Was unable to get the SID')
            print(f'Exception: {e}')

    def get_queries(self):
        if self.pihole_sid is None:
            self.get_sid()

        pihole_response = requests.get(
        f'http://{self.pihole_address}/api/queries',
        headers={
            "X-FTL-SID": sid,
            "X-FTL-CSRF": csrf
            },
        timeout = 5)

        status_code = pihole_response.status_code

        print(f'Status: {status_code} - Data Obtained')

        data_json = pihole_response.json()
        queries = data_json['queries']
        return queries

    def get_domains(self):
        queries = self.__get_queries()

        # Using set method to create object with no duplicates
        domains = set()

        for query in queries:
            domains.add(query['domain'])



