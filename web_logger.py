import paramiko
import re
from datetime import datetime, timedelta


class WebLogger:

    def parse_log_line(self, line):
        timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)', line)
        if not timestamp_match:
            return None
    
        docker_time = timestamp_match.group(1)
    
        try:
            dt_aware = datetime.fromisoformat(docker_time.replace('Z', '')) + timedelta(hours=7)
            timestamp = dt_aware.replace(tzinfo=None)
        except Exception:
            timestamp = None
    
        return {
            'timestamp': timestamp
        }

    def get_post_time(self, ssh_client):
        command = f"docker ps --filter name=swarm_iot_web --format {{{{.Names}}}}"
        web_container_name = ssh_client.run_one_command(command)

        cmd = f'docker logs --timestamps --tail=1 {web_container_name} | grep "POST /api/v1/ctl/"'
    
        logs = ssh_client.run_one_command(cmd)

        if not logs:
            print("Не удалось получить логи")
            return None
    
        requests = []
    
        for line in logs.splitlines():
            parsed = self.parse_log_line(line)
            requests.append(parsed)
    
        if not requests:
            print("POST-запросы не найдены")
            return None
    
        last_request = requests[-1]
        return last_request['timestamp']
    