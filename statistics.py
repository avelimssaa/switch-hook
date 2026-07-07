import time
import threading
from mqtt_logger import MQTTLogger
from web_logger import WebLogger

class Statistics:
    def __init__(self, server, requests_count):
        self.server = server
        self.requests_count = requests_count

    def run_tcpdump_and_wait_for_mqtt(self, result, timeout=10):
        mqtt_logger = MQTTLogger()
        result['mqtt_time'] = mqtt_logger.get_mqtt_time(self.server, timeout=timeout)

    def measure_delay(self, device):
        result_container = {'mqtt_time': None}
        t = threading.Thread(target=self.run_tcpdump_and_wait_for_mqtt, args=(result_container, 10))
        t.start()

        time.sleep(1)

        if device.get_state():
            print("\nВЫКЛЮЧЕНИЕ РОЗЕТКИ...")
            device.set_new_state(False)
        else:
            print("\nВКЛЮЧЕНИЕ РОЗЕТКИ...")
            device.set_new_state(True)
    
        time.sleep(1)
        
        web_logger = WebLogger()

        post_time = web_logger.get_post_time(self.server)

        t.join()

        mqtt_time = result_container['mqtt_time']
        delta = 0
        if post_time and mqtt_time:
        
            print(f"Время HTTP POST: {post_time.strftime('%H:%M:%S.%f')}")
            print(f"Время MQTT: {mqtt_time.strftime('%H:%M:%S.%f')}")
            if mqtt_time > post_time:
                delta = (mqtt_time - post_time).total_seconds()
                print(f"Разница: {delta} сек")
            else:
                # delta = (post_time - mqtt_time).total_seconds()
                print('MQTT-запрос пришел раньше HTTP-запроса.')
                print(f"Разница: {(post_time - mqtt_time).total_seconds()} сек.")
        
        else:
            if not post_time:
                print("Не удалось получить время POST-запроса")
            if not mqtt_time:
                print("Не удалось получить время MQTT-команды")
            return None
    
        return delta
    
    def count_one_device_average(self, device):
        sum = 0
        for i in range(self.requests_count):
            sum += self.measure_delay(device=device)
            time.sleep(1)
        average = sum / self.requests_count
        print(f'Среднее время обработки запроса: {average} сек')
        return average

    def count_devices_average(self, devices):
        devices_count = len(devices)
        devices_averages_sum = 0
        for device in devices:
            devices_averages_sum += self.count_one_device_average(device)
        total_average = devices_averages_sum / devices_count
        print(f'Среднее время отклика: {total_average}')
        