import os
import requests
import json
import re

headers_sekaiviewer = {
    'DNT': '1',
    'Referer': 'https://sekai.best/',
    'cache-control': 'max-age=0',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


async def check_cooldown(session, user_qq, limiter, time):
    if not limiter.check(user_qq):
        await session.finish(f'冷却中(剩余 {int(limiter.left_time(user_qq)) + 1}秒)', at_sender=True)
    limiter.start_cd(user_qq, time)


def check_local_thb_asset(asset_name, status):
    chara_thumbnail_dir = os.path.join(os.path.dirname(__file__), f'thumbnail/chara/{asset_name}_{status}.png')
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'thumbnail/chara')):
        os.makedirs(os.path.join(os.path.dirname(__file__), 'thumbnail/chara'))
    if os.path.exists(chara_thumbnail_dir):
        return True
    else:
        return False


def check_local_card_asset(asset_name, status):
    # status: str normal or after_training
    card_asset_dir = os.path.join(os.path.dirname(__file__),
                                  f'assets/character/member_small/{asset_name}/card_{status}.png')
    if not os.path.exists(os.path.join(os.path.dirname(__file__), f'assets/character/member_small/{asset_name}')):
        os.makedirs(os.path.join(os.path.dirname(__file__), f'assets/character/member_small/{asset_name}'))
    if os.path.exists(card_asset_dir):
        return True
    else:
        return False


def get_card_thb(asset_name, status):
    chara_thumbnail_dir = os.path.join(os.path.dirname(__file__), f'thumbnail/chara/{asset_name}_{status}.png')
    print(f'{asset_name}_{status} to be downloaded:')
    url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/thumbnail/chara_rip/{asset_name}_{status}.png'
    raw_data = requests.get(url, headers=headers_sekaiviewer)
    with open(chara_thumbnail_dir, 'wb') as f:
        f.write(raw_data.content)
    print('succeeded')


def get_card_asset(asset_name, status):
    # status: str normal or after_training
    card_asset_dir = os.path.join(os.path.dirname(__file__),
                                  f'assets/character/member_small/{asset_name}/card_{status}.png')
    print(f'{asset_name}_{status} to be downloaded:')
    asset_url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/character/member_small/{asset_name}_rip/card_{status}.png'
    raw_data = requests.get(asset_url, headers=headers_sekaiviewer)
    with open(card_asset_dir, 'wb') as f:
        f.write(raw_data.content)
    print('succeeded')


def check_local_gacha_banner(gacha_id):
    gacha_banner_dir = os.path.join(os.path.dirname(__file__), f'assets/gacha_banner/banner_gacha{gacha_id}.png')
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'assets/gacha_banner')):
        os.makedirs(os.path.join(os.path.dirname(__file__), 'assets/gacha_banner'))
    if os.path.exists(gacha_banner_dir):
        return True
    else:
        return False


def get_gacha_banner(gacha_id):
    gacha_banner_dir = os.path.join(os.path.dirname(__file__), f'assets/gacha_banner/banner_gacha{gacha_id}.png')
    print(f'banner gacha{gacha_id} to be downloaded:')
    url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/home/banner/banner_gacha{gacha_id}_rip/banner_gacha{gacha_id}.webp'
    raw_data = requests.get(url, headers=headers_sekaiviewer)
    with open(gacha_banner_dir, 'wb') as f:
        f.write(raw_data.content)
    print('succeeded')


def gacha_load_metas():
    gacha_list_dir = os.path.join(os.path.dirname(__file__), '../metas/gacha_list.json')
    master_data_dir = os.path.join(os.path.dirname(__file__), '../metas/master_data.json')
    cards_list_dir = os.path.join(os.path.dirname(__file__), '../metas/cards_list.json')
    with open(gacha_list_dir, 'r') as f:
        gachas = json.load(f)
    with open(master_data_dir, 'r') as f:
        master_data = json.load(f)
    with open(cards_list_dir, 'r') as f:
        cards = json.load(f)
    return gachas, master_data, cards


def game_load_cards():
    cards_list_dir = os.path.join(os.path.dirname(__file__), '../metas/cards_list.json')
    with open(cards_list_dir, 'r') as f:
        cards = json.load(f)
    return cards


def audio_update_aliases():
    url_zh = 'https://i18n-json.sekai.best/zh-CN/music_titles.json'
    url_ja = 'https://i18n-json.sekai.best/ja/music_titles.json'
    raw_data = requests.get(url_zh, headers=headers_sekaiviewer)
    titles_zh = json.loads(raw_data.content)
    raw_data = requests.get(url_ja, headers=headers_sekaiviewer)
    titles_ja = json.loads(raw_data.content)
    index_list = list(titles_ja.keys())
    song_aliases_dir = os.path.join(os.path.dirname(__file__), '../metas/song_aliases.json')
    with open(song_aliases_dir, 'r') as f:
        song_aliases = json.load(f)
    for idx, index in enumerate(index_list):
        if index not in song_aliases.keys():
            if index in titles_zh.keys():
                song_aliases[index] = [titles_ja[index], titles_zh[index]]
            else:
                song_aliases[index] = [titles_ja[index]]
    # print(song_aliases)
    with open(song_aliases_dir, 'w') as f:
        json.dump(song_aliases, f, indent=2, ensure_ascii=False)
    return index_list


def audio_update_list():
    url = 'https://sekai-world.github.io/sekai-master-db-diff/musicVocals.json'
    raw_data = requests.get(url, headers=headers_sekaiviewer)
    vocals_list = json.loads(raw_data.content)
    song_list = []
    asset_list = []
    for idx, item in enumerate(vocals_list):
        asset_name = item['assetbundleName']
        if re.search('short', asset_name) is not None:
            suffix = '.flac'
        else:
            suffix = '_short.flac'
        music_short_dir = os.path.join(os.path.dirname(__file__), f'music/short/{asset_name}/{asset_name}' + suffix)
        asset_list.append(music_short_dir)
        song_list.append(re.search('[0-9]{4}', asset_name).group())
    keys = [str(x) for x in range(len(asset_list))]
    assets = dict(zip(keys, asset_list))
    asset_list_dir = os.path.join(os.path.dirname(__file__), '../metas/asset_list.json')
    with open(asset_list_dir, 'w') as f:
        json.dump(assets, f, indent=2, ensure_ascii=False)
    return song_list, asset_list


def audio_update_assets(asset_list):
    for idx, item in enumerate(asset_list):
        asset_name = item.split('/')[-2]
        # vs_0131_01_short/vs_0131_01_short.flac 激唱
        if re.search('short', asset_name) is not None:
            suffix = '.flac'
        else:
            suffix = '_short.flac'
        music_short_dir = item
        if not os.path.exists(os.path.join(os.path.dirname(__file__), f'music/short/{asset_name}/')):
            os.makedirs(os.path.join(os.path.dirname(__file__), f'music/short/{asset_name}/'))
        if os.path.exists(music_short_dir):
            pass
        else:
            print(asset_name)
            url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/music/short/{asset_name}_rip/{asset_name}{suffix}'
            # url = 'https://assets.pjsek.ai/file/pjsekai-assets/' + path + '/' + asset_name + suffix
            raw_data = requests.get(url, headers=headers_sekaiviewer)
            with open(music_short_dir, 'wb') as f:
                f.write(raw_data.content)
