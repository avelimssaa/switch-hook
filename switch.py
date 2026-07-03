import requests
import json
import time
import web_logger
import mqtt_logger
import threading
from config import URL_POST, HEADERS, URL_GET


def run_tcpdump_and_wait_for_mqtt(result, timeout=10):
    result['mqtt_time'] = mqtt_logger.get_mqtt_time(timeout=timeout)

def check_device_state():
    responce = requests.get(URL_GET, headers=HEADERS)
    responce.raise_for_status()

    data = responce.json()

    channel_1_properties = data["channels"]["1"]["deviceProperties"]

    socket_status = None

    for prop in channel_1_properties:
        if prop['kind'] == "ON_OFF":
            socket_status = prop['value']
            break
    
    if socket_status == "true":
        print('Розетка включена. Отключение.')
        set_device_state(False)



def set_device_state(state: bool):
    
    state_string = ""
    if (state):
        state_string = "true"
    else:
        state_string = "false"
    payload = {"value": state_string}
    
    try:
        response = requests.post(URL_POST, headers=HEADERS, 
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



def measure_delay():
    
    check_device_state()

    time.sleep(1)

    result_container = {'mqtt_time': None}
    t = threading.Thread(target=run_tcpdump_and_wait_for_mqtt, args=(result_container, 10))
    t.start()

    time.sleep(1)

    print("\nВКЛЮЧЕНИЕ РОЗЕТКИ...")
    set_device_state(True)
    
    time.sleep(1)

    post_time = web_logger.get_post_time()

    t.join()

    mqtt_time = result_container['mqtt_time']

    if post_time and mqtt_time:
        
        print(f"Время HTTP POST: {post_time.strftime('%H:%M:%S.%f')}")
        print(f"Время MQTT: {mqtt_time.strftime('%H:%M:%S.%f')}")

        if mqtt_time > post_time:
            delta = (mqtt_time - post_time).total_seconds() * 1000
            print(f"Разница: {delta/1000:.6f} сек")
        else:
            print("MQTT-команда была отправлена ДО HTTP-запроса!")
            print(f"Разница: {(post_time - mqtt_time).total_seconds() * 1000:.6f} мс")
    else:
        if not post_time:
            print("Не удалось получить время POST-запроса")
        if not mqtt_time:
            print("Не удалось получить время MQTT-команды")
    
    print("\nВЫКЛЮЧЕНИЕ РОЗЕТКИ...")
    set_device_state(False)
    
    return post_time, mqtt_time



if __name__ == "__main__":
    measure_delay()
    
