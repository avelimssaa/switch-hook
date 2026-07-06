import requests
from devices_urls_config import user_devices_collect
from config import USERS
from switch import measure_delay


def simulation_average():
    user_devices_collect()

    for user_key in USERS:
        for device in USERS[user_key]['devices']:
            measure_delay(device, USERS[user_key])

if __name__ == "__main__":
    simulation_average()
