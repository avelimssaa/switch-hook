import paramiko
import time

class SSHClient:

    def __init__(self, ip_address, name, password):
        self.ip_address = ip_address
        self.name = name
        self.password = password
        self.client = None
        self.channel = None

    def run_one_command(self, cmd):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
        try:
            client.connect(hostname=self.ip_address, username=self.name, password=self.password)
            stdin, stdout, stderr = client.exec_command(cmd)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8').strip()
            if error:
                print(f'Ошибка: {error}')
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
            client.connect(hostname=self.ip_address, username=self.name, password=self.password, timeout=10)
            transport = client.get_transport()
            channel = transport.open_session()
            channel.get_pty()
            channel.exec_command(cmd)

            self.channel = channel
            self.client = client

            return channel, client
        except Exception as exception:
            print(f"Ошибка подключения: {exception}")
            return None, None
    
    def send_data_from_channel(self, timeout):
        start_time = time.time()
        buffer = ""

        try:
            while time.time() - start_time < timeout:
                if self.channel.recv_ready():
                    data = self.channel.recv(4096).decode('utf-8', errors='ignore')
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
        self.channel.close()
        self.client.close()
