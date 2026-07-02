import requests
import json
import time
import web_logger
import mqtt_logger
import threading
from dotenv import load_dotenv
import os


load_dotenv()

# HOST = "http://192.168.2.110"
HOST = os.getenv('HOST')
# TOKEN = "eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxIiwiYXVkIjoiYW5kcm9pZC1jbGllbnQiLCJ1aWQiOiJlNTM0Y2UwMy0yZDYyLTQwMDMtYWNiYS04NmNjYzI2YWE5YzkiLCJuYmYiOjE3ODI5ODc4NzYsImlzcyI6Imh0dHA6Ly8xOTIuMTY4LjIuMTEwIiwiZXhwIjoxNzgyOTkxNDc2LCJpYXQiOjE3ODI5ODc4NzYsImFpZCI6IjE5ZTFiZjRjLTc3MGUtNGQ2MS05Yzk3LTU5OTVlODcyZjdmMyIsImp0aSI6IjNjYmRkMzEwLTg5NTktNDdiYy1iOTkwLTRiZTdiOGU0MTI0ZCJ9.Ose5V1nTQUIVndZG3lOmURq4Tl9_axshyuuioh7nvzC2CiBTLrXJxhrnvHlzcI0RNeHcyAyWhZOrihP7HtuOe_wrJboJABIqzuu-dHZxdUy7cRwyBctVWRVTzUfKrNFQTPR2qHcny0zwqZeUQ9UobZMLoVv1TJ5vvIMYlwRgO9xB_xTwoGiacT8PN284UuyKW2-FEBOei4TG8wqyGpc9Y_-1JktmXn7dKAtfRCXlm0_ynzz4PWjZId2gTfs3KbL6CODGcyVhAWYGJWCaguNOG0q3s_asLRnaAVfeNhDnadJACnl8NjdbeA8bXC3o3Q5qBax6A3FygsI5mdEikZq9hA"

TOKEN = os.getenv('TOKEN')

PROXY = {
    "http": "http://127.0.0.1:8888",
    "https": "http://127.0.0.1:8888"
}

URL = f"{HOST}/api/v1/ctl/36394e5e-558f-48c1-a738-c681c437d727/devices/e87db5b4-a660-4467-b43c-9d53591e4dc6/props/00250000_0"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

WEB_CONTAINER_NAME = "swarm_iot_web.1.yimyt94ri3m3mtw32yhs0v267"

def run_tcpdump_and_wait_for_mqtt(result, timeout=10):
    result = mqtt_logger.get_mqtt_time(timeout=timeout)


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
    
    mqtt_time = 0
    t = threading.Thread(target=run_tcpdump_and_wait_for_mqtt, args=(mqtt_time, 10))
    t.start()

    time.sleep(0.5)

    print("\nВКЛЮЧЕНИЕ РОЗЕТКИ...")
    set_device_state(True)
    
    time.sleep(1)

    post_time = web_logger.get_post_time()

    t.join()

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
