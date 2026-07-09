from config import HOST
from models.user import User
from statistics_responce import Statistics
from file_writer import FileWriter


def main():

    try:
        requests_count = int(input("Введите количество запросов к устройству: "))
    except:
        print('Введите число больше нуля.')
        return

    if requests_count <= 0:
        print('Введите число больше 0')
        return
    
    file_writer = FileWriter('Socket_logs.txt')
    statistic = Statistics(file_writer, requests_count)
    user1 = User('1', '1', HOST)
    statistic.count_devices_average(user1.get_devices())


if __name__ == "__main__":
    main()
