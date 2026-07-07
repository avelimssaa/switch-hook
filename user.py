import requests
from device import Device


class User:

    def __init__(self, server, username, password, host):
        self.server = server
        self.username = username
        self.password = password
        self.host = host
        self.houses = []
        self.devices = []
        self.access_token = ""
        self.refresh_token = ""
        self.find_devices()
    
    def find_devices(self):
        self.authentication()
        self.get_house_ids()
        for house in self.houses:
            GET_DEVICES_URL = f'{self.host}/api/v1/houses/{house}/devices'

            HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
            }

            responce = requests.get(
            GET_DEVICES_URL,
            headers=HEADERS
            )

            responce.raise_for_status()

            data = responce.json()

            for device in data:
                device_id = device['nodeId']
                controller_id = device['controllerId']

                device_url = f'{self.host}/api/v1/ctl/{controller_id}/devices/{device_id}'
                # print(f'DEVICE URLS: {device_url}')

                user_device = Device(device_url, self.access_token)

                self.devices.append(user_device)

    def get_device_ip_address():
        pass

    def authentication(self):
        AUTH_URL = f'{self.host}/api/v1/oauth2/token'
        responce = requests.post(AUTH_URL, 
                                 params={
        'grant_type': 'password',
        'username': self.username,
        'password': self.password,
        'client_id': 'android-client'
        },
        auth=('android-client', 'password')
                             )
        responce.raise_for_status()
        data = responce.json()

        access_token = data['access_token']
        refresh_token = data['refresh_token']
        self.access_token = access_token
        self.refresh_token = refresh_token

    def get_house_ids(self):

        HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.access_token}"
        }

        GET_HOUSE_URL = f'{self.host}/api/v1/houses'
        
        responce = requests.get(
            GET_HOUSE_URL,
            params={
            'language' : 'ru'
            },
        headers=HEADERS
        )

        responce.raise_for_status()

        data = responce.json()

        house_ids = [house['id'] for house in data]

        self.houses = house_ids

    def check_token():
        pass
