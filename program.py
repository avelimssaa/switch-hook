from ssh_client import SSHClient
from config import SSH_HOST, SSH_PASSWORD, SSH_USERNAME, HOST
from statistics import Statistics
from user import User

def main():

    try:
        requests_count = int(input("Введите количество запросов к устройству: "))
    except:
        print('Введите число.')
        return

    server = SSHClient(SSH_HOST, SSH_USERNAME, SSH_PASSWORD)
    statistic = Statistics(server, requests_count)
    user1 = User(server, '1', '1', HOST)
    statistic.count_devices_average(user1.devices)


if __name__ == "__main__":
    main()