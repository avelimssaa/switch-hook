import requests
import json
import time
import web_logger
import mqtt_logger
import threading


def run_tcpdump_and_wait_for_mqtt(result, timeout=10):
    result['mqtt_time'] = mqtt_logger.get_mqtt_time(timeout=timeout)

def check_device_state(device_url, user_data):
    HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {user_data['token']}"
    }
            
    responce = requests.get(device_url, headers=HEADERS)
    responce.raise_for_status()

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


def set_device_state(state: bool, device_url, user_data):
    
    state_string = ""
    if (state):
        state_string = "true"
    else:
        state_string = "false"
    payload = {"value": state_string}
    
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {user_data['token']}"
    }

    try:
        response = requests.post(f'{device_url}/props/00250000_0', headers=HEADERS, 
                                 json=payload,
                                 timeout=10)
        
        if response.status_code == 204:
            print(f"Устройство {'включено' if state else 'выключено'} (статус: {response.status_code})")
            return True
        else:
            print(f"Ошибка: статус {response.status_code}")
            print(f"Ответ: {response.text}")
            return False

    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return False



def measure_delay(device_url, user_data):

    result_container = {'mqtt_time': None}
    t = threading.Thread(target=run_tcpdump_and_wait_for_mqtt, args=(result_container, 10))
    t.start()

    time.sleep(1)

    if check_device_state(device_url, user_data):
        print("\nВЫКЛЮЧЕНИЕ РОЗЕТКИ...")
        set_device_state(False, device_url, user_data)
    else:
        print("\nВКЛЮЧЕНИЕ РОЗЕТКИ...")
        set_device_state(True, device_url, user_data)
    
    time.sleep(1)

    post_time = web_logger.get_post_time()

    t.join()

    mqtt_time = result_container['mqtt_time']

    if post_time and mqtt_time:
        
        print(f"Время HTTP POST: {post_time.strftime('%H:%M:%S.%f')}")
        print(f"Время MQTT: {mqtt_time.strftime('%H:%M:%S.%f')}")

        if mqtt_time > post_time:
            delta = (mqtt_time - post_time).total_seconds()
            print(f"Разница: {delta} сек")
        else:
            print('MQTT-запрос пришел раньше HTTP-запроса.')
            print(f"Разница: {(post_time - mqtt_time).total_seconds()} сек.")
    else:
        if not post_time:
            print("Не удалось получить время POST-запроса")
        if not mqtt_time:
            print("Не удалось получить время MQTT-команды")
    
    return post_time, mqtt_time


if __name__ == "__main__":
    measure_delay()
    