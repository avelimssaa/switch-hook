import requests


class Device:

    def __init__(self, URL, user_token, IP=None):
        self.__URL = URL
        self.__IP = IP
        self.__user_token = user_token
    
    def get_state(self):
        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.__user_token}"
        }
        
        try:
            responce = requests.get(self.__URL, headers=HEADERS)
            responce.raise_for_status()
        except Exception as exception:
            print(f'Произошла ошибка при запросе статуса: {exception}')
            return None

        data = responce.json()

        channel_1_properties = data["channels"]["1"]["deviceProperties"]

        socket_status = None

        for prop in channel_1_properties:
            if prop['kind'] == "ON_OFF":
                socket_status = prop['value']
                break

        if socket_status == "true":
            return True
        else:
            return False

    def set_new_state(self, state: bool):
        state_string = ""
        if (state):
            state_string = "true"
        else:
            state_string = "false"
        payload = {"value": state_string}
    
        HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.__user_token}"
        }

        try:
            response = requests.post(f'{self.__URL}/props/00250000_0', headers=HEADERS, 
                                 json=payload,
                                 timeout=10)
        
            if response.status_code == 204:
                print(f"Устройство {self.__IP} {'включено' if state else 'выключено'} (статус: {response.status_code})")
                return True
            else:
                print(f"Ошибка: статус {response.status_code}")
                print(f"Ответ: {response.text}")
                return False

        except Exception as exception:
            print(f"Неожиданная ошибка: {exception}")
            return False
 
    def get_ip_address(self):
        return self.__IP
    
    def get_URL(self):
        return self.__URL
    
    def get_user_token(self):
        return self.__user_token

    def set_device_ip(self, IP):
        self.__IP = IP
