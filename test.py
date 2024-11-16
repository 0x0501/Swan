from config import Config
import os
from pathlib import Path
config = Config('./swan.config.toml')

c = config.load()

# print(c['account']['test']['username'])

# c['account']['test']['username'] = 'jjj'
# print(c['account']['test']['username'])
# config.save()

print(c['account']['dzdp']['page_maximum'])


# chrome_executable_path = Path(config['application']['chrome_executable_path'])
# print(os.path.exists(chrome_executable_path))