from ssh_client import SSHClient
from config import SSH_HOST, SSH_PASSWORD, SSH_USERNAME
from statistics import Statistics

def main():
    host = SSHClient(SSH_HOST, SSH_USERNAME, SSH_PASSWORD)
    statistic = Statistics(host)
    statistic.measury_delay()


if __name__ == "__main__":
    main()