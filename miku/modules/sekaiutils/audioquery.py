import random
import shutil

import requests
import json
import re
import os
from fuzzywuzzy import fuzz, process
from nonebot import on_command, on_natural_language, CommandSession, NLPSession, IntentCommand

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
    asset_list_dir = os.path.join(os.path.dirname(__file__), 'asset_list.json')
    with open(asset_list_dir, 'r') as f:
        assets = json.load(f)
    asset = random.sample(list(assets.values()), 1)[0]
    tmp_result_dir = '/home/phynon/opt/cqhttp/data/voices/tmp_result.flac'
    shutil.copy(asset, tmp_result_dir)
    try:
        cq_song_short = f'[CQ:record,file=tmp_result.flac]'
        print(cq_song_short)
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
    song_aliases_dir = os.path.join(os.path.dirname(__file__), 'song_aliases.json')
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
    song_index = ''
    if title in alias_list:
        for idx, item in enumerate(alias_list_raw):
            if title in item:
                song_index = index_list[idx]
                break
        print(f'song {song_index} {title} requested')
        song_index = format(int(song_index), '04d')
    else:
        real_title, confidence = process.extractOne(title, alias_list)
        if confidence < 80:
            await session.send(f'还不会唱{title}')
            await session.send(f'你有{confidence}%的可能在找：{real_title}，\n'
                               + '添加歌曲别名请艾特我发送：\n'
                               + '歌曲标题也叫歌曲别名')
            return
        else:
            for idx, item in enumerate(alias_list_raw):
                if real_title in item:
                    song_index = index_list[idx]
                    break
            print(f'song {song_index} {real_title} alias {title} requested')
            song_index = format(int(song_index), '04d')
    asset_list_dir = os.path.join(os.path.dirname(__file__), 'asset_list.json')
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
        url = 'https://api.pjsek.ai/assets?parent=startapp/music/short&$limit=1000&$sort[isDir]=-1&$sort[path]=1'
        raw_data = requests.get(url)
        data = json.loads(raw_data.content)
        dir_list = data['data']
        song_list = []
        asset_list = []
        for idx, item in enumerate(dir_list):
            path = item['path']
            asset_name = path.split('/')[-1]
            if re.search('short', asset_name) is not None:
                suffix = '.flac'
            else:
                suffix = '_short.flac'
            music_short_dir = os.path.join(os.path.dirname(__file__), f'music/short/{asset_name}/{asset_name}'+suffix)
            asset_list.append(music_short_dir)
            song_list.append(re.search('[0-9]{4}', asset_name).group())
        keys = [str(x) for x in range(len(asset_list))]
        assets = dict(zip(keys, asset_list))
        asset_list_dir = os.path.join(os.path.dirname(__file__), 'asset_list.json')
        with open(asset_list_dir, 'w') as f:
            json.dump(assets, f, indent=2, ensure_ascii=False)

        get_song_info = (f"sekai中现在有{len(set(song_list))}首歌曲，\n"
                         f"有{len(keys)}段不一样的歌声。\n"
                         f"你今天想要听到谁的思念呢？")
        await session.send(get_song_info)
    except Exception as identifier:
        print(identifier)


@on_command('get_song_assets',
            aliases='更新歌曲预览',
            only_to_me=False)
async def get_song_list(session):
    try:
        url = 'https://api.pjsek.ai/assets?parent=startapp/music/short&$limit=1000&$sort[isDir]=-1&$sort[path]=1'
        raw_data = requests.get(url)
        data = json.loads(raw_data.content)
        dir_list = data['data']
        song_list = []
        asset_list = []
        for idx, item in enumerate(dir_list):
            path = item['path']
            asset_name = path.split('/')[-1]
            if re.search('short', asset_name) is not None:
                suffix = '.flac'
            else:
                suffix = '_short.flac'
            asset_url = 'https://assets.pjsek.ai/file/pjsekai-assets/' + path + '/' + asset_name + suffix
            asset_list.append(asset_url)
            song_list.append(re.search('[0-9]{4}', asset_name).group())
        for idx, item in enumerate(asset_list):
            path = dir_list[idx]['path']
            asset_name = path.split('/')[-1]
            if re.search('short', asset_name) is not None:
                suffix = '.flac'
            else:
                suffix = '_short.flac'
            music_short_dir = os.path.join(os.path.dirname(__file__), f'music/short/{asset_name}/{asset_name}' + suffix)
            if not os.path.exists(os.path.join(os.path.dirname(__file__), f'music/short/{asset_name}/')):
                os.makedirs(os.path.join(os.path.dirname(__file__), f'music/short/{asset_name}/'))
            if os.path.exists(music_short_dir):
                pass
            else:
                print(asset_name)
                url =  'https://sekai-res.dnaroma.eu/file/sekai-assets/' + path + '/' + asset_name + suffix
                # url = 'https://assets.pjsek.ai/file/pjsekai-assets/' + path + '/' + asset_name + suffix
                raw_data = requests.get(url, headers=headers_sekaiviewer)
                with open(music_short_dir, 'wb') as f:
                    f.write(raw_data.content)

        await session.send('歌曲文件更新完成')
    except Exception as identifier:
        print(identifier)


@on_command('get_song_titles',
            aliases='更新歌曲标题列表',
            only_to_me=False)
async def get_song_titles(session):
    try:
        url_zh = 'https://i18n-json.sekai.best/zh-CN/music_titles.json'
        url_ja = 'https://i18n-json.sekai.best/ja/music_titles.json'
        raw_data = requests.get(url_zh)
        titles_zh = json.loads(raw_data.content)
        raw_data = requests.get(url_ja)
        titles_ja = json.loads(raw_data.content)
        index_list = list(titles_ja.keys())
        song_aliases_dir = os.path.join(os.path.dirname(__file__), 'song_aliases.json')
        with open(song_aliases_dir, 'r') as f:
            if f.read(1):
                f.seek(0, 0)
                song_aliases = json.load(f)
            else:
                song_aliases = {}
        for idx, index in enumerate(index_list):
            if index not in song_aliases.keys():
                if index in titles_zh.keys():
                    song_aliases[index] = [titles_ja[index], titles_zh[index]]
                else:
                    song_aliases[index] = [titles_ja[index]]
        # print(song_aliases)
        with open(song_aliases_dir, 'w') as f:
            json.dump(song_aliases, f, indent=2, ensure_ascii=False)
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
        song_aliases_dir = os.path.join(os.path.dirname(__file__), 'song_aliases.json')
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
