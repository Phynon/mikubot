import re

SUPERUSERS = {3408828601}
COMMAND_START = ['', re.compile(r'[/!]+')]

MODULES_ON = {'chat', 'sekaievent', 'sekaiutils', 'sekaischeduler'}

# listen to remote cqhttp
HOST = '127.0.0.1'
PORT = 8700
NICKNAME = {'miku'}
SESSION_RUNNING_EXPRESSION = '不要打扰我哦'