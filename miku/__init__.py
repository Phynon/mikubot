import nonebot
import os

from . import config

_bot = None
mikubot = nonebot.NoneBot


def init() -> mikubot:
    global _bot
    nonebot.init(config)
    _bot = nonebot.get_bot()

    for module_name in config.MODULES_ON:
        nonebot.load_plugins(
            os.path.join(os.path.dirname(__file__), 'modules', module_name),
            f'miku.modules.{module_name}')
    return _bot


def get_bot() -> mikubot:
    if _bot is None:
        raise ValueError('Miku has not been initialized')
    return _bot
