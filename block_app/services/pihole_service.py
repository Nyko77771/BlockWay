import requests
import json

class Pihole:

    pihole_address = ''
    pihole_password  = ''
    pihole_sid = ''

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

        except Exception as e:
            print('Was unable to get the SID')
            print(f'Exception: {e}')