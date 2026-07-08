import re
from datetime import datetime, timedelta

from config import SSH_HOST, SSH_PASSWORD, SSH_USERNAME
from ssh_client import SSHClient


class WebLogger:

    def __parse_log_line(self, line):
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

    def get_post_time(self, post_request):
        ssh_client = SSHClient(SSH_HOST, SSH_USERNAME, SSH_PASSWORD)

        command = f"docker ps --filter name=swarm_iot_web --format {{{{.Names}}}}"
        web_container_name = ssh_client.run_one_command(command)
        
        if f'http://{SSH_HOST}/' in post_request:
            post_request = post_request.replace(f'http://{SSH_HOST}/', '/')

        cmd = f'docker logs --timestamps --tail=10 {web_container_name} | grep "{post_request}"'
        logs = ssh_client.run_one_command(cmd)

        if not logs:
            print("Не удалось получить логи")
            return None

        requests = []
    
        for line in logs.splitlines():
            if post_request in line:
                parsed = self.__parse_log_line(line)
                if parsed is not None:
                    requests.append(parsed)
    
        if not requests:
            print("POST-запросы не найдены")
            return None
    
        last_request = requests[-1]
        return last_request['timestamp']
    