import importlib
import os
from nonebot.default_config import *
from .__bot__ import *

# load module configs
for module in MODULES_ON:
    try:
        importlib.import_module('miku.config.' + module)
    except ModuleNotFoundError:
        pass
