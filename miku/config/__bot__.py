import re

SUPERUSERS = {3408828601}
COMMAND_START = ['', re.compile(r'[/!]+')]

MODULES_ON = {'chat', 'sekaievent', 'sekaime'}

# listen to remote cqhttp
HOST = '127.0.0.1'
PORT = 8700
