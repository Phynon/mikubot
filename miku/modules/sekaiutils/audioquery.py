import random
import shutil

import requests
import json
import re
import os
from fuzzywuzzy import process
from nonebot import on_command, on_natural_language, CommandSession, NLPSession, IntentCommand
from miku.modules.sekaiutils import audio_update_aliases
from miku.modules.sekaiutils import audio_update_assets
from miku.modules.sekaiutils import audio_update_list
headers_sekaiviewer = {
    'DNT': '1',
    'Referer': 'https://sekai.best/',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

@on_command('play_song_short',
            aliases=('歌声', '歌曲', '今天打啥歌', '玩啥', '玩什么'),
            only_to_me=False)
async def play_song_short(session):
    asset_list_dir = os.path.join(os.path.dirname(__file__), '../metas/asset_list.json')
    with open(asset_list_dir, 'r') as f:
        assets = json.load(f)
    asset = random.sample(list(assets.values()), 1)[0]
    tmp_result_dir = '/home/phynon/opt/cqhttp/data/voices/tmp_result.flac'
    shutil.copy(asset, tmp_result_dir)
    try:
        cq_song_short = f'[CQ:record,file=tmp_result.flac]'
        print(asset)
        await session.send(cq_song_short)
    except Exception as identifier:
        print(identifier)


@on_natural_language({'唱'}, only_to_me=True)
async def _(session: NLPSession):
    msgs = session.msg.split('唱', 1)
    if len(msgs) == 2:
        return IntentCommand(name=f'request_song_short',
                             current_arg=msgs[1],
                             confidence=100.0)
    else:
        session.send('爬')
        return


@on_command('request_song_short',
            only_to_me=False)
async def request_song_short(session):
    song_aliases_dir = os.path.join(os.path.dirname(__file__), '../metas/song_aliases.json')
    with open(song_aliases_dir, 'r') as f:
        song_aliases = json.load(f)
    index_list = list(song_aliases.keys())
    aliases_list = list(song_aliases.values())
    all_aliases = []
    for item in aliases_list:
        all_aliases += item
    title = session.get('title')
    song_index = ''
    if title in all_aliases:
        for idx, item in enumerate(aliases_list):
            if title in item:
                song_index = index_list[idx]
                break
        print(f'song {song_index} {title} requested')
        song_index = format(int(song_index), '04d')
    else:
        real_title, confidence = process.extractOne(title, all_aliases)
        if confidence < 80:
            await session.send(f'还不会唱{title}')
            await session.send(f'你有{confidence}%的可能在找：{real_title}，\n'
                               + '添加歌曲别名请艾特我发送：\n'
                               + '歌曲标题也叫歌曲别名')
            return
        else:
            for idx, item in enumerate(aliases_list):
                if real_title in item:
                    song_index = index_list[idx]
                    break
            print(f'song {song_index} {real_title} alias {title} requested')
            song_index = format(int(song_index), '04d')
    asset_list_dir = os.path.join(os.path.dirname(__file__), '../metas/asset_list.json')
    with open(asset_list_dir, 'r') as f:
        assets = json.load(f)
    asset_list = list(assets.values())
    request_list = list(filter(lambda x: re.search(song_index, x) is not None, asset_list))
    asset = random.sample(request_list, 1)[0]
    tmp_result_dir = '/home/phynon/opt/cqhttp/data/voices/tmp_result.flac'
    shutil.copy(asset, tmp_result_dir)
    try:
        cq_song_short = f'[CQ:record,file=tmp_result.flac]'
        print(cq_song_short)
        await session.send(cq_song_short)
    except Exception as identifier:
        print(identifier)


@request_song_short.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text
    if session.is_first_run:
        if stripped_arg:
            session.state['title'] = stripped_arg
        else:
            session.finish('爬')
    if not stripped_arg:
        session.finish('爬')
    session.state[session.current_key] = stripped_arg


@on_command('get_song_list',
            aliases='更新歌曲列表',
            only_to_me=False)
async def get_song_list(session):
    try:
        song_list, asset_list = audio_update_assets()
        get_song_info = (f"sekai中现在有{len(set(song_list))}首歌曲，\n"
                         f"有{len(asset_list)}段不一样的歌声。\n"
                         f"你今天想要听到谁的思念呢？")
        await session.send(get_song_info)
    except Exception as identifier:
        print(identifier)


@on_command('get_song_assets',
            aliases='更新歌曲预览',
            only_to_me=False)
async def get_song_assets(session):
    try:
        song_list, asset_list = audio_update_list()
        get_song_info = (f"sekai中现在有{len(set(song_list))}首歌曲，\n"
                         f"有{len(asset_list)}段不一样的歌声。\n"
                         f"你今天想要听到谁的思念呢？")
        await session.send(get_song_info)
        audio_update_assets(asset_list)
        await session.send('歌曲文件更新完成')
    except Exception as identifier:
        print(identifier)


@on_command('get_song_titles',
            aliases='更新歌曲标题列表',
            only_to_me=False)
async def get_song_titles(session):
    try:
        index_list = audio_update_aliases()
        get_titles_info = (f"sekai中现在有{len(index_list)}首歌曲。\n"
                           f"添加歌曲别名请艾特我发送：\n"
                           f"歌曲标题也叫歌曲别名")
        await session.send(get_titles_info)
    except Exception as identifier:
        print(identifier)


@on_natural_language({'也叫'}, only_to_me=True)
async def _(session: NLPSession):
    return IntentCommand(name='add_song_alias',
                         current_arg=session.msg,
                         confidence=100.0)


@on_command('add_song_alias', aliases=['add'], only_to_me=False)
async def add_song_alias(session):
    try:
        song_aliases_dir = os.path.join(os.path.dirname(__file__), '../metas/song_aliases.json')
        with open(song_aliases_dir, 'r') as f:
            if f.read(1):
                f.seek(0, 0)
                song_aliases = json.load(f)
            else:
                song_aliases = {}
        index_list = list(song_aliases.keys())
        alias_list_raw = list(song_aliases.values())
        alias_list = []
        for item in alias_list_raw:
            alias_list += item
        title = session.get('title')
        alias = session.get('alias')
        if title in alias_list:
            if alias in alias_list:
                await session.send('早就知道啦~')
            else:
                song_index = ''
                for idx, item in enumerate(alias_list_raw):
                    if title in item:
                        song_index = index_list[idx]
                        break
                print(f'alias of song {song_index} {title} added')
                song_aliases[song_index].append(alias)
                with open(song_aliases_dir, 'w') as f:
                    json.dump(song_aliases, f, indent=2, ensure_ascii=False)
                await session.send('知道啦~')
        else:
            real_title, confidency = process.extractOne(title, alias_list)
            await session.send(f'你有{confidency}%的可能在找：{real_title}')
    except Exception as identifier:
        print(identifier)
        await session.send(identifier)


@add_song_alias.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.split('也叫')
    print(stripped_arg)
    if session.is_first_run:
        if len(stripped_arg) == 2:
            session.state['title'] = stripped_arg[0].strip()
            session.state['alias'] = stripped_arg[1].strip()
        else:
            session.finish('爬')
    if not stripped_arg:
        session.finish('爬')
    session.state[session.current_key] = stripped_arg
