import paramiko
import re
from datetime import datetime, timedelta
from config import SSH_HOST, SSH_PASSWORD, SSH_USERNAME, WEB_CONTAINER_NAME


def execute_remote_command(host, username, password, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(hostname=host, username=username, password=password)
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8')
        return output
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
    finally:
        client.close()

def parse_log_line(line):
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


def parse_logs_for_requests(log_text):
    requests = []
    
    for line in log_text.splitlines():
        parsed = parse_log_line(line)
        requests.append(parsed)
    
    return requests


def get_post_time():

    cmd = f'docker logs --timestamps --tail=1 {WEB_CONTAINER_NAME} | grep "POST /api/v1/ctl/"'
    
    logs = execute_remote_command(SSH_HOST, SSH_USERNAME, SSH_PASSWORD, cmd)

    if not logs:
        print("Не удалось получить логи")
        return None
    
    requests = parse_logs_for_requests(logs)
    
    if not requests:
        print("POST-запросы не найдены")
        return None
    
    last_request = requests[-1]
    return last_request['timestamp']
