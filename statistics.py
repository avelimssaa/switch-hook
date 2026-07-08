import time
import threading
import queue
from mqtt_logger import MQTTLogger
from web_logger import WebLogger

class Statistics:
    def __init__(self, requests_count=5):
        self.__requests_count = requests_count

    def __run_tcpdump_and_wait_for_mqtt(self, result, device_ip, timeout=10):
        mqtt_logger = MQTTLogger()
        result['mqtt_time'] = mqtt_logger.get_mqtt_time(device_ip, timeout=timeout)

    def __measure_delay(self, device):

        result_container = {'mqtt_time': None}
        t = threading.Thread(target=self.__run_tcpdump_and_wait_for_mqtt, args=(result_container, device.IP, 10))
        t.start()

        time.sleep(1)

        if device.get_state():
            print("\nВЫКЛЮЧЕНИЕ РОЗЕТКИ...")
            device.set_new_state(False)
        else:
            print("\nВКЛЮЧЕНИЕ РОЗЕТКИ...")
            device.set_new_state(True)
        
        web_logger = WebLogger()

        post_time = web_logger.get_post_time(device.URL)
        t.join()

        mqtt_time = result_container['mqtt_time']
        delta = 0
        if post_time and mqtt_time:
        
            print(f"Время HTTP POST {device.IP}: {post_time.strftime('%H:%M:%S.%f')}")
            print(f"Время MQTT {device.IP}: {mqtt_time.strftime('%H:%M:%S.%f')}")
            if mqtt_time > post_time:
                delta = (mqtt_time - post_time).total_seconds()
                print(f"Разница для {device.IP}: {delta} сек")
            else:
                pass
                delta = (post_time - mqtt_time).total_seconds()
                print(f'MQTT-запрос для {device.IP} пришел раньше HTTP-запроса.')
                # print(f"Разница: {(post_time - mqtt_time).total_seconds()} сек.")
        
        else:
            if not post_time:
                print("Не удалось получить время POST-запроса")
            if not mqtt_time:
                print("Не удалось получить время MQTT-команды")
            return None
    
        return delta
    
    def __count_one_device_average(self, device):
        sum = 0
        for _ in range(self.__requests_count):
            sum += self.__measure_delay(device=device)
            time.sleep(1)
        average = sum / self.__requests_count
        # print(f'Среднее время обработки запроса: {average} сек')
        return average


    def __run_count_device_average_in_thread(self, result_queue, device):
        result = self.__count_one_device_average(device=device)
        result_queue.put((device.IP, result))


    def count_devices_average(self, devices):
        devices_count = len(devices)
        devices_averages_sum = 0

        result_queue = queue.Queue()
        threads = []
        for device in devices:
            thread = threading.Thread(target=self.__run_count_device_average_in_thread, args=(result_queue, device), name=f'Thread device IP: {device.IP}')
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        for _ in range(len(threads)):
            device_ip, result = result_queue.get()
            print(f'Средняя задержка устройства с IP-адресом {device_ip}: {result} сек')
            devices_averages_sum += result


        # for device in devices:
        #     devices_averages_sum += self.count_one_device_average(device)

        total_average = devices_averages_sum / devices_count
        print(f'Среднее время отклика: {total_average} сек')
