import paramiko
import time

class SSHClient:

    def __init__(self, ip_address, name, password):
        self.__ip_address = ip_address
        self.__name = name
        self.__password = password
        self.__client = None
        self.__channel = None

    def run_one_command(self, cmd):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
        try:
            client.connect(hostname=self.__ip_address, username=self.__name, password=self.__password)
            _, stdout, _ = client.exec_command(cmd)
            output = stdout.read().decode('utf-8')
            return output or None
        except Exception as exception:
            print(f"Ошибка: {exception}")
            return None
        finally:
            client.close()
    
    def run_continuous_command(self, cmd):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
        try:
            client.connect(hostname=self.__ip_address, username=self.__name, password=self.__password, timeout=10)
            transport = client.get_transport()
            channel = transport.open_session()
            channel.get_pty()
            channel.exec_command(cmd)

            self.__channel = channel
            self.__client = client

            return channel, client
        except Exception as exception:
            print(f"Ошибка подключения: {exception}")
            return None, None
    
    def send_data_from_channel(self, timeout):
        start_time = time.time()
        buffer = ""

        try:
            while time.time() - start_time < timeout:
                if self.__channel.recv_ready():
                    data = self.__channel.recv(4096).decode('utf-8', errors='ignore')
                    buffer += data
                
                    lines = buffer.split('\n')
                    buffer = lines[-1]

                    return lines
                time.sleep(0.1)
        
            print(f"Таймаут ({timeout} сек).")
            return None
        
        except KeyboardInterrupt:
            print("\nПрервано пользователем")
            return None
    
    def close_channel(self):
        self.__channel.close()
        self.__client.close()
    
    def get_ip_address(self):
        return self.__ip_address
    
    def get_username(self):
        return self.__name
    
    def get_password(self):
        return self.__password
