import paramiko
import re
from datetime import datetime, timezone, timedelta
from config import SSH_HOST, SSH_PASSWORD, SSH_USERNAME, WEB_CONTAINER_NAME


LOCAL_OFFSET = timedelta(hours=7)
LOCAL_TZ = timezone(LOCAL_OFFSET)

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


def get_recent_logs(host, username, password, container_name, lines=100):
    cmd = f'docker logs --timestamps --tail={lines} {container_name} | grep "POST /api/v1/ctl/"'
    return execute_remote_command(host, username, password, cmd)


def parse_log_line(line):
    timestamp_match = re.match(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)', line)
    if not timestamp_match:
        return None
    
    docker_time = timestamp_match.group(1)
    
    url_match = re.search(r'"(POST|GET|PUT|DELETE) (/[^"]+)"', line)
    if not url_match:
        return None
    
    method = url_match.group(1)
    url = url_match.group(2)
    
    status_match = re.search(r'"\s+(\d{3})\s+', line)
    status_code = status_match.group(1) if status_match else None

    try:
        dt_aware = datetime.fromisoformat(docker_time.replace('Z', '+00:00'))
        timestamp = dt_aware.replace(tzinfo=None)
    except Exception:
        timestamp = None
    
    return {
        'timestamp': timestamp,
        'time_str': docker_time,
        'method': method,
        'url': url,
        'status_code': status_code,
        'raw': line
    }


def parse_logs_for_requests(log_text):
    requests = []
    
    for line in log_text.splitlines():
        parsed = parse_log_line(line)
        if parsed and parsed['method'] == 'POST' and '/api/v1/ctl/' in parsed['url']:
            requests.append(parsed)
    
    return requests


def get_post_time():
    logs = get_recent_logs(SSH_HOST, SSH_USERNAME, SSH_PASSWORD, WEB_CONTAINER_NAME, lines=100)
    
    if not logs:
        print("Не удалось получить логи")
        return None
    
    requests = parse_logs_for_requests(logs)
    
    if not requests:
        print("POST-запросы не найдены")
        return None
    
    last_request = requests[-1]
    return last_request['timestamp']
