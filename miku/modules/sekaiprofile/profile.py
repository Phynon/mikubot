import json
import os
from typing import FrozenSet

import requests
from nonebot import CommandSession, on_command


@on_command('sekaime', aliases=('sekaime'), only_to_me=False)
async def sekaime_react(session):
    try:
        src = 'https://mo.zju.edu.cn/pyapi/apps/run/5fc78a949a6edafe98c1f3a7'
        uid = session.get('uid')
        print(uid)
        url = src + '/api/user/${uid}/profile'
        response = requests.post(url, uid)
        data = json.loads(response.content)
        print(data)
        # await session.send(data)
    except KeyError as identifier:
        await session.send('セカイようこそ！')
    else:
        pass


@sekaime_react.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['uid'] = stripped_arg
        return
    if not stripped_arg:
        session.pause('セカイようこそ！')
    session.state[session.current_key] = stripped_arg
