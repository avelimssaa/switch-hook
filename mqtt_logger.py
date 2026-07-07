import re
from datetime import datetime, timedelta
from config import MQTT_DESTINATION_HOST


class MQTTLogger:

    def parse_tcpdump_time(self, line):
        match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)', line)
        if match:
            try:
                return datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S.%f") + timedelta(hours=7)
            except ValueError:
                return None
        return None

    def get_mqtt_time(self, ssh_client ,timeout=10):

        # cmd = f"echo '{ssh_client.password}' | sudo -S tcpdump -i enp0s3 -tttt -n -s 0 -A -l  'src host {ssh_client.ip_address} and dst host {MQTT_DESTINATION_HOST} and tcp port 8883'   | grep --line-buffered 'length 117'"
        cmd = f"echo '{ssh_client.password}' | sudo -S tcpdump -i enp0s3 -tttt -n -s 0 -A -l  'src host {ssh_client.ip_address} and tcp port 8883'   | grep --line-buffered 'length 117'"
    
        channel, client = ssh_client.run_continuous_command(cmd)
    
        if not channel:
            print("Не удалось запустить tcpdump")
            return None
        
        attempts_count = 0

        while attempts_count < 10:
            lines = ssh_client.send_data_from_channel(timeout)
            for line in lines:
                datetime = self.parse_tcpdump_time(line)
                if datetime:
                    ssh_client.close_channel()
                    return datetime
        
        return None

