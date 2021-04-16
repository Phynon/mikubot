import json
import os
from typing import FrozenSet

import requests
from nonebot import CommandSession, on_command

players_dir = os.path.join(os.path.dirname(__file__), 'known_players.json')
with open(players_dir, 'r') as f:
    if f.read(1):
        f.seek(0, 0)
        players = json.load(f)
    else:
        players = {}


@on_command('myrank', aliases='sekairank', only_to_me=False)
async def myrank_react(session):
    try:
        src = 'http://183.173.139.67:5000/myrank'
        uid = session.get('uid')
        rq = {'uid': uid}
        response = requests.post(src, rq)
        # print(response.content)
        data = json.loads(response.content)
        data = data['rankings'][0]
        ranking = (f"玩家名 {data['name']}\n"
                   f"好友码 {data['userId']}\n"
                   f"分数    {data['score']}\n"
                   f"排名    {data['rank']}")
        await session.send(ranking)
    except Exception as identifier:
        print(identifier)
        await session.send(identifier)
    else:
        pass


@myrank_react.args_parser

async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.event['sender']['user_id'] is not None:
        user_qq = str(session.event['sender']['user_id'])
    else:
        user_qq = str(session.event['user_id'])
    flag = (user_qq in players.keys())
    if session.is_first_run:
        if stripped_arg:
            session.state['uid'] = stripped_arg
            if not flag:
                players[user_qq] = stripped_arg
                with open(players_dir, 'w') as f:
                    json.dump(players, f, indent=2)
            return
    if not stripped_arg:
        if flag:
            print(flag)
            session.state['uid'] = players[user_qq]
            return
        else:
            session.pause('セカイへようこそ！\n'
                          + '初次见面，请发送\n'
                          + '"myrank 好友码"\n'
                          + '来告诉您的信息！')
    session.state[session.current_key] = stripped_arg
