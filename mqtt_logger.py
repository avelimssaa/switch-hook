import paramiko
import re
import time
from datetime import datetime
from config import SSH_HOST, SSH_PASSWORD, SSH_USERNAME, MQTT_DESTINATION_HOST


def execute_remote_command_async(host, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f'SSHHOST: {SSH_HOST}')
    try:
        client.connect(hostname=host, username=username, password=password, timeout=10)
        transport = client.get_transport()
        channel = transport.open_session()
        
        channel.get_pty()
        channel.exec_command(command)
        return channel, client
    except Exception as e:
        print(f"Ошибка подключения: {e}")
        return None, None


def parse_tcpdump_time(line):
    match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)', line)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S.%f")
        except ValueError:
            return None
    return None


def get_mqtt_time(timeout=10):

    cmd = f"echo '{SSH_PASSWORD}' | sudo -S tcpdump -i enp0s3 -tttt -n -s 0 -A -l  'src host {SSH_HOST} and dst host {MQTT_DESTINATION_HOST} and tcp port 8883'   | grep --line-buffered 'length 117'"
    
    channel, client = execute_remote_command_async(
        SSH_HOST, SSH_USERNAME, SSH_PASSWORD, cmd
    )
    
    if not channel:
        print("Не удалось запустить tcpdump")
        return None
    
    start_time = time.time()
    buffer = ""
    
    try:
        while time.time() - start_time < timeout:
            if channel.recv_ready():
                data = channel.recv(4096).decode('utf-8', errors='ignore')
                buffer += data
                
                lines = buffer.split('\n')
                buffer = lines[-1]
                
                for line in lines[:-1]:
                    if 'length 117' in line:
                        dt = parse_tcpdump_time(line)
                        if dt:
                            print(f"Найдена MQTT-команда: {dt.strftime('%H:%M:%S.%f')[:-3]}")
                            print(f"Строка: {line.strip()}")
                            return dt
            
            time.sleep(0.1)
        
        print(f"Таймаут ({timeout} сек). MQTT-команда не обнаружена")
        return None
        
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
        return None
    finally:
        channel.close()
        client.close()
        print("tcpdump остановлен")
