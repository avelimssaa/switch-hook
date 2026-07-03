from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv('HOST')

TOKEN = os.getenv('TOKEN')

PROXY = {
    "http": "http://127.0.0.1:8888",
    "https": "http://127.0.0.1:8888"
}

URL_POST = f"{HOST}/api/v1/ctl/36394e5e-558f-48c1-a738-c681c437d727/devices/e87db5b4-a660-4467-b43c-9d53591e4dc6/props/00250000_0"
URL_GET = f"{HOST}/api/v1/ctl/36394e5e-558f-48c1-a738-c681c437d727/devices/e87db5b4-a660-4467-b43c-9d53591e4dc6"

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

WEB_CONTAINER_NAME = "swarm_iot_web.1.yrvfrgo5syt62bvxxebzbnc29"

SSH_HOST = os.getenv('SSH_HOST')
SSH_USERNAME = os.getenv('SSH_USERNAME')
SSH_PASSWORD = os.getenv('SSH_PASSWORD')
