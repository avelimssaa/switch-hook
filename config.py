import os

from dotenv import load_dotenv

load_dotenv()

HOST = os.getenv('HOST')

PROXY = {
    "http": "http://127.0.0.1:8888",
    "https": "http://127.0.0.1:8888"
}

SSH_HOST = os.getenv('SSH_HOST')
SSH_USERNAME = os.getenv('SSH_USERNAME')
SSH_PASSWORD = os.getenv('SSH_PASSWORD')
