import json
import os

import requests
from nonebot import CommandSession, on_command

players_dir = os.path.join(os.path.dirname(__file__), '../sekaievent/known_players.json')
with open(players_dir, 'r') as f:
    if f.read(1):
        f.seek(0, 0)
        players = json.load(f)
    else:
        players = {}


@on_command('myprofile', aliases=['me', 'profile'], only_to_me=False)
async def myprofile(session):
    try:
        src = 'http://183.173.141.23:5000/profile'
        uid = session.get('uid')
        rq = {'uid': uid}
        print(rq)
        response = requests.post(src, rq)
        print(response.content)
        data = json.loads(response.content)
        data = data['userProfile']['word']
        ranking = (data)
        await session.send(ranking)
    except Exception as identifier:
        print(identifier)
        await session.send(identifier)
    else:
        pass


@myprofile.args_parser
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
            session.finish('セカイへようこそ！\n'
                           + '初次见面，请发送\n'
                           + '"myrank 好友码"\n'
                           + '来告诉您的信息！')
    session.state[session.current_key] = stripped_arg


@on_command('mysongs', aliases=['查歌'], only_to_me=False)
async def mysongs(session):
    try:
        src = 'http://183.173.141.23:5000/profile'
        uid = session.get('uid')
        rq = {'uid': uid}
        print(rq)
        response = requests.post(src, rq)
        print(response.content)
        data = json.loads(response.content)
        data = data['userProfile']['word']
        ranking = (data)
        await session.send(ranking)
    except Exception as identifier:
        print(identifier)
        await session.send(identifier)
    else:
        pass


@mysongs.args_parser

async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.event['sender']['user_id'] is not None:
        user_qq = str(session.event['sender']['user_id'])
    else:
        user_qq = str(session.event['user_id'])
    flag = (user_qq in players.keys())
    if flag:
        print(flag)
        session.state['uid'] = players[user_qq]
    else:
        session.finish('セカイへようこそ！\n'
                       + '初次见面，请发送\n'
                       + '"myrank 好友码"\n'
                       + '来告诉您的信息！')
    if session.is_first_run:
        if stripped_arg:
            if flag:
                print(flag)
                session.state['uid'] = players[user_qq]
                return
            else:
                session.finish('セカイへようこそ！\n'
                               + '初次见面，请发送\n'
                               + '"myrank 好友码"\n'
                               + '来告诉您的信息！')
    if not stripped_arg:
        session.pause('爬')
    session.state[session.current_key] = stripped_arg