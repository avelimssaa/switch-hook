from dotenv import load_dotenv
import os
import requests
import paramiko

load_dotenv()

HOST = os.getenv('HOST')

PROXY = {
    "http": "http://127.0.0.1:8888",
    "https": "http://127.0.0.1:8888"
}

URL_POST = f"{HOST}/api/v1/ctl/36394e5e-558f-48c1-a738-c681c437d727/devices/e87db5b4-a660-4467-b43c-9d53591e4dc6/props/00250000_0"
URL_GET = f"{HOST}/api/v1/ctl/36394e5e-558f-48c1-a738-c681c437d727/devices/e87db5b4-a660-4467-b43c-9d53591e4dc6"
AUTH_URL = f'{HOST}/api/v1/oauth2/token'

def get_token(AUTH_URL):
    responce = requests.post(AUTH_URL, 
                                 params={
        'grant_type': 'password',
        'username': '1',
        'password': '1',
        'client_id': 'android-client'
    },
    auth=('android-client', 'password')
                             )

    data = responce.json()

    token = data['access_token']

    return token


TOKEN = get_token(AUTH_URL=AUTH_URL)

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

SSH_HOST = os.getenv('SSH_HOST')
SSH_USERNAME = os.getenv('SSH_USERNAME')
SSH_PASSWORD = os.getenv('SSH_PASSWORD')

def get_container_name():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=SSH_HOST, username=SSH_USERNAME, password=SSH_PASSWORD)
        command = f"docker ps --filter name=swarm_iot_web --format {{{{.Names}}}}"

        stdin, stdout, stderr = client.exec_command(command)
        
        container_name = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()

        if error:
            print(f'Ошибка: {error}')

        return container_name or None
    finally:
        client.close()

# WEB_CONTAINER_NAME = "swarm_iot_web.1.r1yxa6mdxtt8s4gscexjr41e5"

WEB_CONTAINER_NAME = get_container_name()

MQTT_DESTINATION_HOST=os.getenv('MQTT_DESTINATION_HOST')
