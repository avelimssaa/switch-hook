import threading
import time

import requests

from loggers.mqtt_logger import MQTTLogger
from models.device import Device


class User:

    def __init__(self, username, password, host):
        self.__username = username
        self.__password = password
        self.__host = host
        self.__houses = []
        self.__devices = []
        self.__access_token = ""
        self.__find_devices()
    
    def __run_tcpdump_and_wait_for_ip_address(self, result, timeout=10):
        mqtt_logger = MQTTLogger()
        result['ip_address'] = mqtt_logger.get_mqtt_ip_address_dest(timeout)


    def __find_devices(self):
        self.__authentication()
        self.__get_house_ids()
        for house in self.__houses:
            GET_DEVICES_URL = f'{self.__host}/api/v1/houses/{house}/devices'

            HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.__access_token}"
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

                device_url = f'{self.__host}/api/v1/ctl/{controller_id}/devices/{device_id}'
                user_device = Device(device_url, self.__access_token)
                device = self.__get_device_ip_address(user_device)
                self.__devices.append(user_device)

    def __get_device_ip_address(self, device):
        result_container = {'ip_address': None}
        t = threading.Thread(target=self.__run_tcpdump_and_wait_for_ip_address, args=(result_container, 10))

        t.start()

        time.sleep(1)

        if device.get_state():
            print("\nВЫКЛЮЧЕНИЕ РОЗЕТКИ...")
            device.set_new_state(False)
        else:
            print("\nВКЛЮЧЕНИЕ РОЗЕТКИ...")
            device.set_new_state(True)
        
        time.sleep(1)

        t.join()

        device.set_device_ip(result_container['ip_address'])

        print(f'DEVICE IP: {device.get_ip_address()}')
        print(f'DEVICE URL: {device.get_URL()}')

        return device


    def __authentication(self):
        
        AUTH_URL = f'{self.__host}/api/v1/oauth2/token'
        responce = requests.post(AUTH_URL, 
                                 params={
        'grant_type': 'password',
        'username': self.__username,
        'password': self.__password,
        'client_id': 'android-client'
        },
        auth=('android-client', 'password')
                             )
        
        responce.raise_for_status()
        data = responce.json()

        access_token = data['access_token']

        self.__access_token = access_token
        

    def __get_house_ids(self):

        HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.__access_token}"
        }

        GET_HOUSE_URL = f'{self.__host}/api/v1/houses'
        
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

        self.__houses = house_ids
    
    def get_devices(self):
        return self.__devices
    