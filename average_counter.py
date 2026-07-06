import requests
from devices_urls_config import user_devices_collect
from config import USERS


def simulation_average():
    user_devices_collect()

    for user_key in USERS:
        for device in USERS[user_key]['devices']:
            pass

if __name__ == "__main__":
    simulation_average()
