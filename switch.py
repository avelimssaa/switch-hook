import requests
import json
import time
import web_logger
import mqtt_logger
import threading
from config import URL, HEADERS


def run_tcpdump_and_wait_for_mqtt(result, timeout=10):
    result['mqtt_time'] = mqtt_logger.get_mqtt_time(timeout=timeout)


def set_device_state(state: bool):
    
    state_string = ""
    if (state):
        state_string = "true"
    else:
        state_string = "false"
    payload = {"value": state_string}
    
    try:
        response = requests.post(URL, headers=HEADERS, 
                                 json=payload, 
                                 # proxies=PROXY, 
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
    
    result_container = {'mqtt_time': None}
    t = threading.Thread(target=run_tcpdump_and_wait_for_mqtt, args=(result_container, 10))
    t.start()

    time.sleep(0.5)

    print("\nВКЛЮЧЕНИЕ РОЗЕТКИ...")
    set_device_state(True)
    
    time.sleep(1)

    post_time = web_logger.get_post_time()

    t.join()

    mqtt_time = result_container['mqtt_time']

    print(f'MQTT time: {mqtt_time}')

    if post_time and mqtt_time:
        print(f"Время HTTP POST: {post_time.strftime('%H:%M:%S.%f')[:-3]}")
        print(f"Время MQTT: {mqtt_time.strftime('%H:%M:%S.%f')[:-3]}")
        
        if mqtt_time > post_time:
            delta = (mqtt_time - post_time).total_seconds() * 1000
            print(f"Задержка: {delta:.0f} мс ({delta/1000:.3f} сек)")
        else:
            print("MQTT-команда была отправлена ДО HTTP-запроса!")
            print(f"Разница: {(post_time - mqtt_time).total_seconds() * 1000:.0f} мс")
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
