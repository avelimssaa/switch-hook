import re
from datetime import datetime, timedelta
from ssh_client import SSHClient
from config import SSH_HOST, SSH_PASSWORD, SSH_USERNAME

class MQTTLogger:

    def parse_tcpdump_time(self, line):
        match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)', line)
        if match:
            try:
                return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S.%f") + timedelta(hours=7)
            except ValueError:
                return None
        return None

    def parse_ip_address(self, line):
        match = re.search(r'>\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\.\d+', line)
        if match:
            return match.group(1)
        else:
            return None

    def get_mqtt_time(self, ssh_client, device_ip, timeout=10):
        
        ssh_client = SSHClient(SSH_HOST, SSH_USERNAME, SSH_PASSWORD)

        cmd = f"echo '{ssh_client.password}' | sudo -S tcpdump -i enp0s3 -tttt -n -s 0 -A -l  'src host {ssh_client.ip_address} and dst host {device_ip} and tcp port 8883'   | grep --line-buffered 'length 117'"
        # cmd = f"echo '{ssh_client.password}' | sudo -S tcpdump -i enp0s3 -tttt -n -s 0 -A -l  'src host {ssh_client.ip_address} and tcp port 8883'   | grep --line-buffered 'length 117'"
    
        channel, _ = ssh_client.run_continuous_command(cmd)
    
        if not channel:
            print("Не удалось запустить tcpdump")
            return None
        
        attempts_count = 0

        while attempts_count < 10:
            lines = ssh_client.send_data_from_channel(timeout)
            if lines is not None:
                for line in lines:
                    # print(f"DEVICE IP:{device_ip}. Пойманные строки: {line}")
                    if device_ip in line:
                        # print(f'DEVICE IP: {device_ip} .Обработанные строки: {line}')
                        datetime = self.parse_tcpdump_time(line)
                        if datetime:
                            ssh_client.close_channel()
                            return datetime
                    # datetime = self.parse_tcpdump_time(line)
                    # if datetime:
                    #     ssh_client.close_channel()
                    #     return datetime
            attempts_count += 1
        
        return None
    
    def get_mqtt_ip_address_dest(self, ssh_client, timeout=10):
        cmd = f"echo '{ssh_client.password}' | sudo -S tcpdump -i enp0s3 -tttt -n -s 0 -A -l  'src host {ssh_client.ip_address} and tcp port 8883'   | grep --line-buffered 'length 117'"

        channel, _ = ssh_client.run_continuous_command(cmd)
    
        if not channel:
            print("Не удалось запустить tcpdump")
            return None
        
        attempts_count = 0

        while attempts_count < 10:
            lines = ssh_client.send_data_from_channel(timeout)
            if lines is not None:
                for line in lines:
                    ip_address = self.parse_ip_address(line)
                    if ip_address:
                        ssh_client.close_channel()
                        return ip_address
            attempts_count += 1
        
        return None

