import queue
import threading
import time

from loggers.mqtt_logger import MQTTLogger
from loggers.web_logger import WebLogger
from file_writer import FileWriter


class Statistics:
    def __init__(self, log_file, requests_count=5):
        self.__requests_count = requests_count
        self.__log_file = log_file


    def __run_tcpdump_and_wait_for_mqtt(self, result, device_ip, timeout=10):
        mqtt_logger = MQTTLogger()
        result['mqtt_time'] = mqtt_logger.get_mqtt_time(device_ip, timeout=timeout)

    def __measure_delay(self, device, log_file):

        result_container = {'mqtt_time': None}
        t = threading.Thread(target=self.__run_tcpdump_and_wait_for_mqtt, args=(result_container, device.get_ip_address(), 3))
        t.start()

        # log_file = FileWriter(f'Logs device with IP: {device.get_ip_address()}')

        time.sleep(1)
        
        get_device_state_attempts = 5
        device_state = device.get_state()
        while get_device_state_attempts > 0:
            if device_state is not None:
                if device.get_state():
                    # print("\nВЫКЛЮЧЕНИЕ РОЗЕТКИ...")
                    log_file.log("\nВЫКЛЮЧЕНИЕ РОЗЕТКИ...\n")
                    device.set_new_state(False)
                else:
                    # print("\nВКЛЮЧЕНИЕ РОЗЕТКИ...")
                    log_file.log("\nВКЛЮЧЕНИЕ РОЗЕТКИ...\n")
                    device.set_new_state(True)
                break
            else:
                get_device_state_attempts -= 1
                device_state = device.get_state()

        if device_state is None:
            return 10
        
        web_logger = WebLogger()

        post_time = web_logger.get_post_time(device.get_URL())
        t.join()

        mqtt_time = result_container['mqtt_time']
        delta = 0
        if post_time and mqtt_time:
        
            # print(f"Время HTTP POST {device.get_ip_address()}: {post_time.strftime('%H:%M:%S.%f')}")
            log_file.log(f"Время HTTP POST {device.get_ip_address()}: {post_time.strftime('%H:%M:%S.%f')}\n")
            # print(f"Время MQTT {device.get_ip_address()}: {mqtt_time.strftime('%H:%M:%S.%f')}")
            log_file.log(f"Время MQTT {device.get_ip_address()}: {mqtt_time.strftime('%H:%M:%S.%f')}\n")
            if mqtt_time > post_time:
                delta = (mqtt_time - post_time).total_seconds()
                # print(f"Разница для {device.get_ip_address()}: {delta} сек")
                log_file.log(f"Разница для {device.get_ip_address()}: {delta} сек\n")
            else:
                delta = (post_time - mqtt_time).total_seconds()
                # print(f'MQTT-запрос для {device.get_ip_address()} пришел раньше HTTP-запроса.')
                log_file.log(f'MQTT-запрос для {device.get_ip_address()} пришел раньше HTTP-запроса.\n')
                # print(f"Разница для {device.get_ip_address()}: {(post_time - mqtt_time).total_seconds()} сек.")
                log_file.log(f"Разница для {device.get_ip_address()}: {(post_time - mqtt_time).total_seconds()} сек.\n")
        
        else:
            if not post_time:
                print("Не удалось получить время POST-запроса")
            if not mqtt_time:
                print("Не удалось получить время MQTT-команды")
            return None
    
        return delta
    
    def __count_one_device_average(self, device, log_file):
        sum = 0
        for _ in range(self.__requests_count):
            dif = self.__measure_delay(device, log_file)
            if dif is not None:
                sum += dif
            else:
                sum += 1
            time.sleep(1)
        average = sum / self.__requests_count
        return average


    def __run_count_device_average_in_thread(self, result_queue, device, log_file):
        result = self.__count_one_device_average(device, log_file)
        result_queue.put((device.get_ip_address(), result))


    def count_devices_average(self, devices):
        devices_count = len(devices)
        devices_averages_sum = 0

        result_queue = queue.Queue()
        threads = []
        for device in devices:
            log_file = FileWriter(f'Logs device with IP: {device.get_ip_address()}')
            thread = threading.Thread(target=self.__run_count_device_average_in_thread, args=(result_queue, device, log_file), name=f'Thread device IP: {device.get_ip_address()}')
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        for _ in range(len(threads)):
            device_ip, result = result_queue.get()
            print(f'\nСредняя задержка устройства с IP-адресом {device_ip}: {result} сек')
            self.__log_file.log(f'\nСредняя задержка устройства с IP-адресом {device_ip}: {result} сек\n')
            devices_averages_sum += result

        total_average = devices_averages_sum / devices_count
        print(f'\nСреднее время отклика: {total_average} сек')
        self.__log_file.log(f'\nСреднее время отклика: {total_average} сек')

