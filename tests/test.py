import os
import sys
from pathlib import Path
sys.path.append(os.path.split(sys.path[0])[0])
from src.utils.config import Config

config = Config('./swan.config.toml')

c = config.load()

# print(c['account']['test']['username'])

# c['account']['test']['username'] = 'jjj'
# print(c['account']['test']['username'])
# config.save()

print(c['account']['dzdp']['page_maximum'])
print(Path.joinpath(Path(c['application']['data_directory']), 'dazhongdianping.xlsx'))

sd = 'sdsdsds'
s = [sd]
print(s)
print(sd)

# chrome_executable_path = Path(config['application']['chrome_executable_path'])
# print(os.path.exists(chrome_executable_path))