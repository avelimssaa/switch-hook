import time
from datetime import datetime

class FileWriter:
    
    def __init__(self, file_name):
        self.__file_name = file_name
        self.init_log()


    def log(self, string):
        with open(f'logs/{self.__file_name}', 'a') as file:
            file.write(string)
    
    def init_log(self):
        self.log('\n')
        self.log('=' * 100)
        self.log('\n\n')
        self.log(f'\nNEW MEASUREMENT at {datetime.fromtimestamp(time.time())}\n')
        self.log('\n')
        self.log('=' * 100)
        self.log('\n')
