from ssh_client import SSHClient
from config import SSH_HOST, SSH_PASSWORD, SSH_USERNAME, HOST
from statistics import Statistics
from user import User

def main():
    server = SSHClient(SSH_HOST, SSH_USERNAME, SSH_PASSWORD)
    statistic = Statistics(server, 10)
    user1 = User(server, '1', '1', HOST)
    statistic.count_one_device_average(user1.devices[0])


if __name__ == "__main__":
    main()