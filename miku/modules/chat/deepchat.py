import random
import os

import json
import re

import nonebot
import requests
from nonebot import on_command, on_natural_language, NLPSession, IntentCommand, CommandSession
from miku.utils import check_favor, favor_up, favor_down

"""
@on_natural_language(only_to_me=True)
async def _(session: NLPSession):
    return IntentCommand(60.0, 'ai_deepchat', args={'message': session.msg_text})


@on_command('ai_deepchat')
async def ai_deepchat(session: CommandSession):
    message = session.state.get('message')
    reply = await call_qingyunke_api(message)
    # await session.send(reply)


async def call_qingyunke_api(message: str):
    params = {
        'key': 'free',
        'appid': 0,
        'msg': message
    }
    try:
        url = 'http://api.qingyunke.com/api.php'
        raw_data = requests.get(url, params=params)
        data = json.loads(raw_data.content)
        if data['result'] == 0:
            content = data['content']
            if '菲菲' in content:
                content = content.replace('菲菲', 'miku')
            if '艳儿' in content:
                content = content.replace('艳儿', 'miku')
            if '公众号' in content:
                content = ''
            if '{br}' in content:
                content = content.replace('{br}', '\n')
            if '提示' in content:
                content = content[: content.find('提示')]
            if '淘宝' in content:
                content = ''
            if '發msg咯' in content:
                    content = ''
            while True:
                r = re.search('{face:(.*)}', content)
                if r:
                    id_ = r.group(1)
                    print(content)
                    content = ''
                else:
                    break
        return (
            await check_text(content)
        )
    except Exception as identifier:
        print(identifier)

async def check_text(text: str) -> str:
    # ALAPI improper reply text check
    params = {'token': '3gZi3jWVbafEqkCs', 'text': text}
    check_url = 'https://v2.alapi.cn/api/censor/text'
    try:
        data = (requests.get(check_url, timeout=2, params=params)).json()
        if data['code'] == 200:
            if data['data']['conclusion_type'] == 2:
                return ''
    except Exception as e:
        print(f'检测违规文本错误...{type(e)}：{e}')
    return text
"""