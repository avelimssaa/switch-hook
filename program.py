from config import HOST
from statistics import Statistics
from user import User


def main():

    try:
        requests_count = int(input("Введите количество запросов к устройству: "))
    except:
        print('Введите число.')
        return

    statistic = Statistics(requests_count)
    user1 = User('1', '1', HOST)
    statistic.count_devices_average(user1.get_devices())


if __name__ == "__main__":
    main()