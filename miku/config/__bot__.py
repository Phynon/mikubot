import re

SUPERUSERS = {3408828601}
COMMAND_START = ['', re.compile(r'[/!]+')]

MODULES_ON = {'chat'}

# listen to remote cqhttp
HOST = '0.0.0.0'
PORT = 5700
