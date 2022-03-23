import json
import time
import os
import random
import re

import requests
import textwrap
import asyncio
import nest_asyncio
import httpx
from PIL import Image, ImageDraw, ImageFont
from miku.utils import FreqLimiter
from nonebot import CommandSession, on_command
from nonebot.command import _FinishException

nest_asyncio.apply()

limiter = FreqLimiter(10)

headers_sekaiviewer = {
    'DNT': '1',
    'Referer': 'https://sekai.best/',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

headers_pjsekai = {
    'DNT': '1',
    'Referer': 'https://pjsek.ai/',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


async def prepare_honor_images(profile_honor: dict) -> tuple:
    """
    [
        {'bondsHonorWordId': 0, 'honorId': 105, 'honorLevel': 1, 'profileHonorType': 'normal', 'seq': 1},
        {'bondsHonorViewType': 'normal', 'bondsHonorWordId': 1012101, 'honorId': 1012101, 'honorLevel': 1, 'profileHonorType': 'bonds', 'seq': 2},
        {'bondsHonorViewType': 'none', 'bondsHonorWordId': 0, 'honorId': 97, 'honorLevel': 1, 'profileHonorType': 'normal', 'seq': 3}
    ]
    """
    print('prepare honor data')
    honor_meta_url = 'https://sekai-world.github.io/sekai-master-db-diff/honors.json'
    raw_data = requests.get(honor_meta_url, headers=headers_sekaiviewer)
    honor_data = json.loads(raw_data.content)
    honor_groups_url = 'https://sekai-world.github.io/sekai-master-db-diff/honorGroups.json'
    raw_data = requests.get(honor_groups_url, headers=headers_sekaiviewer)
    honor_groups_data = json.loads(raw_data.content)
    honor_keys = [item['id'] for item in honor_data]
    honor_metas = dict(zip(honor_keys, honor_data))
    honor_groups_keys = [item['id'] for item in honor_groups_data]
    honor_groups = dict(zip(honor_groups_keys, honor_groups_data))
    honor_thumbnails = []
    honor_rarities = []
    honor_names = []

    print(profile_honor)

    for i in range(3):
        if f'honorId{i + 1}' not in profile_honor:
            image = Image.new('RGBA', [1, 1])
            honor_thumbnails.append(image)
            honor_names.append('')
            honor_rarities.append('')
            continue
        honor_id = profile_honor[f'honorId{i + 1}']
        honor_id = format(int(honor_id), '04d')
        honor_asset_name = honor_metas[int(honor_id)]['assetbundleName']
        honor_group_id = honor_metas[int(honor_id)]['groupId']
        if 'backgroundAssetbundleName' in honor_groups[int(honor_group_id)]:
            honor_asset_name = honor_groups[int(honor_group_id)]['backgroundAssetbundleName']
        if not os.path.exists(
                os.path.join(
                    os.path.dirname(__file__),
                    f'assets/honor/{honor_asset_name}/degree_main.png')):
            if not os.path.exists(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/honor/{honor_asset_name}')):
                os.mkdir(
                    os.path.join(os.path.dirname(__file__),
                                 f'assets/honor/{honor_asset_name}'))
            asset_url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/honor/{honor_asset_name}_rip/degree_main.png'
            raw_data = requests.get(asset_url, headers=headers_sekaiviewer)
            with open(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/honor/{honor_asset_name}/degree_main.png'),
                    'wb') as f:
                f.write(raw_data.content)
        image = Image.open(
            os.path.join(os.path.dirname(__file__),
                         f'assets/honor/{honor_asset_name}/degree_main.png'))
        honor_thumbnails.append(image)
        honor_names.append(honor_metas[int(honor_id)]['name'])
        honor_rarities.append(honor_metas[int(honor_id)]['honorRarity'])

    return honor_thumbnails, honor_names, honor_rarities


async def get_card_assets(client, user_cards: list, deck_assets: dict, card_id: int, idx: int, deck_images: list, leader: list):
    default_image = user_cards[idx]['defaultImage']
    assetbundle_name = deck_assets[str(card_id)]

    if default_image == 'original':
        asset_url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/character/member_cutout/{assetbundle_name}_rip/normal.png'
        if not os.path.exists(
                os.path.join(
                    os.path.dirname(__file__),
                    f'assets/character/member_cutout/{assetbundle_name}/normal/normal.png'
                )):
            if not os.path.exists(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}'
                    )):
                os.mkdir(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}'
                    ))
            if not os.path.exists(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}/normal'
                    )):
                os.mkdir(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}/normal'
                    ))
            raw_data = httpx.get(asset_url, headers=headers_sekaiviewer)
            with open(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}/normal/normal.png'
                    ), 'wb') as f:
                f.write(raw_data.content)
        image = Image.open(
            os.path.join(
                os.path.dirname(__file__),
                f'assets/character/member_cutout/{assetbundle_name}/normal/normal.png'
            ))
        deck_images.append(image)
        if idx == 0:
            asset_url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/character/member_small/{assetbundle_name}_rip/card_normal.png'
            if not os.path.exists(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_small/{assetbundle_name}/card_normal.png'
                    )):
                if not os.path.exists(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_small/{assetbundle_name}'
                        )):
                    os.mkdir(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_small/{assetbundle_name}'
                        ))
                raw_data = httpx.get(asset_url, headers=headers_sekaiviewer)
                with open(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_small/{assetbundle_name}/card_normal.png'
                        ), 'wb') as f:
                    f.write(raw_data.content)
            leader.append(Image.open(
                os.path.join(
                    os.path.dirname(__file__),
                    f'assets/character/member_small/{assetbundle_name}/card_normal.png'
                )))
    else:
        asset_url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/character/member_cutout/{assetbundle_name}_rip/after_training.png'
        if not os.path.exists(
                os.path.join(
                    os.path.dirname(__file__),
                    f'assets/character/member_cutout/{assetbundle_name}/after_training/after_training.png'
                )):
            if not os.path.exists(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}'
                    )):
                os.mkdir(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}'
                    ))
            if not os.path.exists(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}/after_training'
                    )):
                os.mkdir(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}/after_training'
                    ))
            raw_data = httpx.get(asset_url, headers=headers_sekaiviewer)
            with open(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}/after_training/after_training.png'
                    ), 'wb') as f:
                f.write(raw_data.content)
        image = Image.open(
            os.path.join(
                os.path.dirname(__file__),
                f'assets/character/member_cutout/{assetbundle_name}/after_training/after_training.png'
            ))
        deck_images.append(image)
        if idx == 0:
            asset_url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/character/member_small/{assetbundle_name}_rip/card_after_training.png'
            if not os.path.exists(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_small/{assetbundle_name}/card_after_training.png'
                    )):
                if not os.path.exists(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_small/{assetbundle_name}'
                        )):
                    os.mkdir(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_small/{assetbundle_name}'
                        ))
                raw_data = httpx.get(asset_url, headers=headers_sekaiviewer)
                with open(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_small/{assetbundle_name}/card_after_training.png'
                        ), 'wb') as f:
                    f.write(raw_data.content)
            leader.append(Image.open(
                os.path.join(
                    os.path.dirname(__file__),
                    f'assets/character/member_small/{assetbundle_name}/card_after_training.png'
                )))
    print(idx)

async def prepare_deck_images(data: dict) -> tuple:
    print('prepare deck data')
    cards_list_dir = os.path.join(os.path.dirname(__file__),
                                  '../metas/cards_list.json')
    with open(cards_list_dir, 'r', encoding='utf-8') as f:
        cards = json.load(f)
    deck_list = []
    deck_assets = {}
    deck_images = []
    deck_rarities = {}
    deck_frame_ids = []
    user_cards = []
    time.sleep(0.01)
    for idx in range(5):
        deck_list.append(data['userDecks'][0][f'member{idx + 1}'])
        for card in data['userCards']:
            if card['cardId'] == data['userDecks'][0][f'member{idx + 1}']:
                user_cards.append(card)
    for idx, card in enumerate(cards):
        if card['id'] in deck_list:
            deck_assets[f"{card['id']}"] = card['assetbundleName']
            deck_rarities[f"{card['id']}"] = card['cardRarityType']
    leader = []
    async with httpx.AsyncClient() as client:
        tasks = []
        for idx, card_id in enumerate(deck_list):
            frame_rarity_id = deck_rarities[str(card_id)].split('_')[1]
            deck_frame_ids.append(frame_rarity_id)
            coro = get_card_assets(client, user_cards, deck_assets, card_id, idx, deck_images, leader)
            tasks.append(asyncio.create_task(coro))
    await asyncio.gather(*tasks)
    """
    for idx, card_id in enumerate(deck_list):
        default_image = user_cards[idx]['defaultImage']
        assetbundle_name = deck_assets[str(card_id)]
        deck_frame_ids.append(deck_rarities[str(card_id)])
        if default_image == 'original':
            asset_url = f'https://assets.pjsek.ai/file/pjsekai-assets/startapp/character/member_cutout/{assetbundle_name}/normal/normal.png'
            if not os.path.exists(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}/normal/normal.png'
                    )):
                if not os.path.exists(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_cutout/{assetbundle_name}'
                        )):
                    os.mkdir(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_cutout/{assetbundle_name}'
                        ))
                if not os.path.exists(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_cutout/{assetbundle_name}/normal'
                        )):
                    os.mkdir(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_cutout/{assetbundle_name}/normal'
                        ))
                raw_data = requests.get(asset_url, headers=headers_pjsekai)
                with open(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_cutout/{assetbundle_name}/normal/normal.png'
                        ), 'wb') as f:
                    f.write(raw_data.content)
            image = Image.open(
                os.path.join(
                    os.path.dirname(__file__),
                    f'assets/character/member_cutout/{assetbundle_name}/normal/normal.png'
                ))
            deck_images.append(image)
            if idx == 0:
                asset_url = f'https://assets.pjsek.ai/file/pjsekai-assets/startapp/character/member_small/{assetbundle_name}/card_normal.png'
                if not os.path.exists(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_small/{assetbundle_name}/card_normal.png'
                        )):
                    if not os.path.exists(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_small/{assetbundle_name}'
                            )):
                        os.mkdir(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_small/{assetbundle_name}'
                            ))
                    raw_data = requests.get(asset_url, headers=headers_pjsekai)
                    with open(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_small/{assetbundle_name}/card_normal.png'
                            ), 'wb') as f:
                        f.write(raw_data.content)
                leader = Image.open(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_small/{assetbundle_name}/card_normal.png'
                    ))
        else:
            asset_url = f'https://assets.pjsek.ai/file/pjsekai-assets/startapp/character/member_cutout/{assetbundle_name}/after_training/after_training.png'
            if not os.path.exists(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}/after_training/after_training.png'
                    )):
                if not os.path.exists(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_cutout/{assetbundle_name}'
                        )):
                    os.mkdir(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_cutout/{assetbundle_name}'
                        ))
                if not os.path.exists(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_cutout/{assetbundle_name}/after_training'
                        )):
                    os.mkdir(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_cutout/{assetbundle_name}/after_training'
                        ))
                raw_data = requests.get(asset_url, headers=headers_pjsekai)
                with open(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_cutout/{assetbundle_name}/after_training/after_training.png'
                        ), 'wb') as f:
                    f.write(raw_data.content)
            image = Image.open(
                os.path.join(
                    os.path.dirname(__file__),
                    f'assets/character/member_cutout/{assetbundle_name}/after_training/after_training.png'
                ))
            deck_images.append(image)
            if idx == 0:
                asset_url = f'https://assets.pjsek.ai/file/pjsekai-assets/startapp/character/member_small/{assetbundle_name}/card_after_training.png'
                if not os.path.exists(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_small/{assetbundle_name}/card_after_training.png'
                        )):
                    if not os.path.exists(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_small/{assetbundle_name}'
                            )):
                        os.mkdir(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_small/{assetbundle_name}'
                            ))
                    raw_data = requests.get(asset_url, headers=headers_pjsekai)
                    with open(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_small/{assetbundle_name}/card_after_training.png'
                            ), 'wb') as f:
                        f.write(raw_data.content)
                leader = Image.open(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_small/{assetbundle_name}/card_after_training.png'
                    ))
        """
    return deck_images, deck_frame_ids, leader

@on_command('myprofile', aliases=['me', 'profile'], only_to_me=False)
async def myprofile(session):
    try:
        # 'Connection': 'close'
        src = 'http://127.0.0.1:5000/profile'
        uid = session.get('uid')
        if not limiter.check('profile'):
            await session.finish(f"冷却中(剩余 {int(limiter.left_time('profile')) + 1}秒)", at_sender=True)
        limiter.start_cd('profile', 60)
        rq = {'uid': uid}
        response = requests.post(src, rq)
        print(rq)
        # print(response.content)
        data = json.loads(response.content)
        profile = data['userProfile']
        print(data['userProfileHonors'])
        bg_list = [
            '01_01', '01_02', '02_01', '02_02', '03_01', '03_02', '04_01',
            '04_02', '05_01', '05_02', '06_01', '06_02'
        ]
        honor_coro = prepare_honor_images(profile)
        deck_coro = prepare_deck_images(data)
        loop = asyncio.get_event_loop()
        tasks = [loop.create_task(honor_coro), loop.create_task(deck_coro)]
        loop.run_until_complete(asyncio.wait(tasks))
        try:
            honor_thumbnails, honor_names, honor_rarities = tasks[0].result()
            deck_images, deck_frame_ids, leader = tasks[1].result()
        except Exception as identifier:
            print(repr(identifier))
            print(identifier)

        """
        # honor data
        print('prepare honor data')
        honor_meta_url = 'https://sekai-world.github.io/sekai-master-db-diff/honors.json'
        raw_data = requests.get(honor_meta_url, headers=headers_sekaiviewer)
        honor_data = json.loads(raw_data.content)
        honor_groups_url = 'https://sekai-world.github.io/sekai-master-db-diff/honorGroups.json'
        raw_data = requests.get(honor_groups_url, headers=headers_sekaiviewer)
        honor_groups_data = json.loads(raw_data.content)
        # honorGroups.json
        # honor_metas_dir = os.path.join(os.path.dirname(__file__),
        #                                'honors.json')
        # with open(honor_metas_dir, 'r', encoding='utf-8') as f:
        #     honor_data = json.load(f)
        # honor_groups_dir = os.path.join(os.path.dirname(__file__),
        #                                 'honor_groups.json')
        # with open(honor_groups_dir, 'r', encoding='utf-8') as f:
        #     honor_groups_data = json.load(f)
        honor_keys = [item['id'] for item in honor_data]
        honor_metas = dict(zip(honor_keys, honor_data))
        honor_groups_keys = [item['id'] for item in honor_groups_data]
        honor_groups = dict(zip(honor_groups_keys, honor_groups_data))
        honor_thumbnails = []
        honor_rarities = []
        honor_names = []

        for i in range(3):
            if f'honorId{i + 1}' not in profile:
                image = Image.new('RGBA', [1, 1])
                honor_thumbnails.append(image)
                honor_names.append('')
                honor_rarities.append('')
                continue
            honor_id = profile[f'honorId{i + 1}']
            honor_id = format(int(honor_id), '04d')
            honor_asset_name = honor_metas[int(honor_id)]['assetbundleName']
            honor_group_id = honor_metas[int(honor_id)]['groupId']
            if 'backgroundAssetbundleName' in honor_groups[int(honor_group_id)]:
                honor_asset_name = honor_groups[int(honor_group_id)]['backgroundAssetbundleName']
            if not os.path.exists(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/honor/{honor_asset_name}/degree_main.png')):
                if not os.path.exists(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/honor/{honor_asset_name}')):
                    os.mkdir(
                        os.path.join(os.path.dirname(__file__),
                                     f'assets/honor/{honor_asset_name}'))
                asset_url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/honor/{honor_asset_name}_rip/degree_main.png'
                raw_data = requests.get(asset_url, headers=headers_sekaiviewer)
                with open(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/honor/{honor_asset_name}/degree_main.png'),
                        'wb') as f:
                    f.write(raw_data.content)
            image = Image.open(
                os.path.join(os.path.dirname(__file__),
                             f'assets/honor/{honor_asset_name}/degree_main.png'))
            honor_thumbnails.append(image)
            honor_names.append(honor_metas[int(honor_id)]['name'])
            honor_rarities.append(honor_metas[int(honor_id)]['honorRarity'])
        """
        """
        # deck data
        print('prepare deck data')
        cards_list_dir = os.path.join(os.path.dirname(__file__),
                                      'cards_list.json')
        with open(cards_list_dir, 'r', encoding='utf-8') as f:
            cards = json.load(f)
        deck_list = []
        deck_assets = {}
        deck_images = []
        deck_rarities = {}
        deck_frame_ids = []
        user_cards = []
        time.sleep(0.01)
        for idx in range(5):
            deck_list.append(data['userDecks'][0][f'member{idx + 1}'])
            for card in data['userCards']:
                if card['cardId'] == data['userDecks'][0][f'member{idx + 1}']:
                    user_cards.append(card)
        for idx, card in enumerate(cards):
            if card['id'] in deck_list:
                deck_assets[f"{card['id']}"]  = card['assetbundleName']
                deck_rarities[f"{card['id']}"] = card['rarity']

        for idx, card_id in enumerate(deck_list):
            default_image = user_cards[idx]['defaultImage']
            assetbundle_name = deck_assets[str(card_id)]
            deck_frame_ids.append(deck_rarities[str(card_id)])
            if default_image == 'original':
                asset_url = f'https://assets.pjsek.ai/file/pjsekai-assets/startapp/character/member_cutout/{assetbundle_name}/normal/normal.png'
                if not os.path.exists(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_cutout/{assetbundle_name}/normal/normal.png'
                        )):
                    if not os.path.exists(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_cutout/{assetbundle_name}'
                            )):
                        os.mkdir(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_cutout/{assetbundle_name}'
                            ))
                    if not os.path.exists(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_cutout/{assetbundle_name}/normal'
                            )):
                        os.mkdir(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_cutout/{assetbundle_name}/normal'
                            ))
                    raw_data = requests.get(asset_url, headers=headers_pjsekai)
                    with open(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_cutout/{assetbundle_name}/normal/normal.png'
                            ), 'wb') as f:
                        f.write(raw_data.content)
                image = Image.open(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}/normal/normal.png'
                    ))
                deck_images.append(image)
                if idx == 0:
                    asset_url = f'https://assets.pjsek.ai/file/pjsekai-assets/startapp/character/member_small/{assetbundle_name}/card_normal.png'
                    if not os.path.exists(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_small/{assetbundle_name}/card_normal.png'
                            )):
                        if not os.path.exists(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    f'assets/character/member_small/{assetbundle_name}'
                                )):
                            os.mkdir(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    f'assets/character/member_small/{assetbundle_name}'
                                ))
                        raw_data = requests.get(asset_url, headers=headers_pjsekai)
                        with open(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    f'assets/character/member_small/{assetbundle_name}/card_normal.png'
                                ), 'wb') as f:
                            f.write(raw_data.content)
                    leader = Image.open(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_small/{assetbundle_name}/card_normal.png'
                        ))
            else:
                asset_url = f'https://assets.pjsek.ai/file/pjsekai-assets/startapp/character/member_cutout/{assetbundle_name}/after_training/after_training.png'
                if not os.path.exists(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_cutout/{assetbundle_name}/after_training/after_training.png'
                        )):
                    if not os.path.exists(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_cutout/{assetbundle_name}'
                            )):
                        os.mkdir(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_cutout/{assetbundle_name}'
                            ))
                    if not os.path.exists(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_cutout/{assetbundle_name}/after_training'
                            )):
                        os.mkdir(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_cutout/{assetbundle_name}/after_training'
                            ))
                    raw_data = requests.get(asset_url, headers=headers_pjsekai)
                    with open(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_cutout/{assetbundle_name}/after_training/after_training.png'
                            ), 'wb') as f:
                        f.write(raw_data.content)
                image = Image.open(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/member_cutout/{assetbundle_name}/after_training/after_training.png'
                    ))
                deck_images.append(image)
                if idx == 0:
                    asset_url = f'https://assets.pjsek.ai/file/pjsekai-assets/startapp/character/member_small/{assetbundle_name}/card_after_training.png'
                    if not os.path.exists(
                            os.path.join(
                                os.path.dirname(__file__),
                                f'assets/character/member_small/{assetbundle_name}/card_after_training.png'
                            )):
                        if not os.path.exists(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    f'assets/character/member_small/{assetbundle_name}'
                                )):
                            os.mkdir(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    f'assets/character/member_small/{assetbundle_name}'
                                ))
                        raw_data = requests.get(asset_url, headers=headers_pjsekai)
                        with open(
                                os.path.join(
                                    os.path.dirname(__file__),
                                    f'assets/character/member_small/{assetbundle_name}/card_after_training.png'
                                ), 'wb') as f:
                            f.write(raw_data.content)
                    leader = Image.open(
                        os.path.join(
                            os.path.dirname(__file__),
                            f'assets/character/member_small/{assetbundle_name}/card_after_training.png'
                        ))
        """
        # music data
        print('prepare music data')
        musics = data['userMusics']
        clear = [0, 0, 0, 0, 0]
        fc = [0, 0, 0, 0, 0]
        fp = [0, 0, 0, 0, 0]
        for music in musics:
            statuses = music['userMusicDifficultyStatuses']
            for idx, difficulty in enumerate(statuses):
                results = difficulty['userMusicResults']
                status = {0}
                for result in results:
                    if result['playResult'] == 'full_perfect':
                        status.add(3)
                    elif result['playResult'] == 'full_combo':
                        status.add(2)
                    elif result['playResult'] == 'clear':
                        status.add(1)
                    else:
                        status.add(0)
                if max(status) == 3:
                    clear[idx] += 1
                    fc[idx] += 1
                    fp[idx] += 1
                elif max(status) == 2:
                    clear[idx] += 1
                    fc[idx] += 1
                elif max(status) == 1:
                    clear[idx] += 1
                else:
                    pass
        music_status = [clear, fc, fp]
        bg = random.sample(bg_list, 1)[0]
        # bg = '04_01'
        tmp = Image.open(
            os.path.join(os.path.dirname(__file__),
                         f'assets/background/android_bg_unit{bg}.png'))
        word = profile['word']
        font_t_jp = ImageFont.truetype(
            os.path.join(os.path.dirname(__file__),
                         'assets/fonts/BIZ-UDPGothicB.ttf'), 50)
        font_t_en = ImageFont.truetype(
            os.path.join(os.path.dirname(__file__),
                         'assets/fonts/BIZ-UDPGothicB.ttf'), 45)
        font_t2_en = ImageFont.truetype(
            os.path.join(os.path.dirname(__file__),
                         'assets/fonts/BIZ-UDPGothicB.ttf'), 30)
        font_c_jp = ImageFont.truetype(
            os.path.join(os.path.dirname(__file__),
                         'assets/fonts/BIZ-UDPGothicB.ttf'), 35)
        font_c_en = ImageFont.truetype(
            os.path.join(os.path.dirname(__file__),
                         'assets/fonts/BIZ-UDPGothicB.ttf'), 26)
        draw = ImageDraw.Draw(tmp)

        # challange data
        challange_result = data['userChallengeLiveSoloResults']
        challange_ranks = []
        for i in range(26):
            challange_ranks.append(1)
        for idx, rank in enumerate(data['userChallengeLiveSoloStages']):
            chara_id = rank['characterId']
            if rank['rank'] > challange_ranks[chara_id - 1]:
                challange_ranks[chara_id - 1] = rank['rank']
        best_rank_ids = [
            i for i, val in enumerate(challange_ranks)
            if (val == max(challange_ranks))
        ]
        best_rank_id = random.sample(best_rank_ids, 1)[0]

        # chara data
        print('prepare chara data')
        chara_ranks = []
        for i in range(26):
            chara_ranks.append(0)
        for idx, rank in enumerate(data['userCharacters']):
            if idx == rank['characterId'] - 1:
                chara_ranks[idx] = rank['characterRank']


        print('prepare image')
        print('prepare profile')
        # part 1 profile
        # title border
        draw.rounded_rectangle(xy=[62, 100, 1302, 180],
                               radius=20,
                               fill='#39c5bb',
                               outline=None,
                               width=3)
        draw.text(xy=(92, 60),
                  text='PROFILE',
                  fill='#39c5bb',
                  font=font_t_en,
                  stroke_width=1)
        # title
        draw.rounded_rectangle(xy=[60, 100, 1300, 180],
                               radius=20,
                               fill='#444466',
                               outline=None,
                               width=3)
        draw.text(xy=(90, 115),
                  text='プロファイル',
                  fill='#ffffff',
                  font=font_t_jp,
                  stroke_width=0)
        draw.text(xy=(90, 60),
                  text='PROFILE',
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1)
        # main
        leader = leader[0].resize((600, 338), Image.ANTIALIAS)
        # print(leader.size)
        mask = Image.new('RGBA', (600, 338))
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle(xy=[0, 0, 600, 338],
                                    radius=15,
                                    fill='#ffffe0',
                                    outline='#e6e6e6',
                                    width=3)
        tmp.paste(im=leader, box=(80, 210), mask=mask)
        draw.rounded_rectangle(xy=[80, 210, 680, 548],
                               radius=15,
                               fill=None,
                               outline='#e6e6e6',
                               width=3)
        draw.rounded_rectangle(xy=[720, 210, 1280, 548],
                               radius=20,
                               fill='#ffffe0',
                               outline='#e6e6e6',
                               width=3)
        draw.rounded_rectangle(xy=[740, 229, 920, 289],
                               radius=30,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3)
        draw.rounded_rectangle(xy=[740, 309, 920, 369],
                               radius=30,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3)
        draw.rounded_rectangle(xy=[740, 389, 920, 449],
                               radius=30,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3)
        draw.rounded_rectangle(xy=[740, 469, 920, 529],
                               radius=30,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3)
        draw.text(xy=(780, 245),
                  text='NAME',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1)
        draw.text(xy=(798, 325),
                  text='UID',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1)
        draw.text(xy=(780, 405),
                  text='RANK',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1)
        draw.text(xy=(755, 485),
                  text='TWITTER',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1)
        draw.text(xy=(940, 240),
                  text=data['user']['userGamedata']['name'],
                  fill='#444466',
                  font=font_c_jp,
                  stroke_width=1)
        draw.text(xy=(940, 327),
                  text=str(data['user']['userGamedata']['userId']),
                  fill='#444466',
                  font=font_c_en,
                  stroke_width=1)
        draw.text(xy=(940, 400),
                  text=str(data['user']['userGamedata']['rank']),
                  fill='#444466',
                  font=font_c_jp,
                  stroke_width=1)
        draw.text(xy=(940, 480),
                  text=data['userProfile']['twitterId'],
                  fill='#444466',
                  font=font_c_jp,
                  stroke_width=1)
        # part 2 honorI
        print('prepare honor')
        # title border
        draw.rounded_rectangle(xy=[62, 610, 1302, 690],
                               radius=20,
                               fill='#39c5bb',
                               outline=None,
                               width=3)
        draw.text(xy=(92, 570),
                  text='HONOR',
                  fill='#39c5bb',
                  font=font_t_en,
                  stroke_width=1)
        # title
        draw.rounded_rectangle(xy=[60, 610, 1300, 690],
                               radius=20,
                               fill='#444466',
                               outline=None,
                               width=3)
        draw.text(xy=(90, 625),
                  text='称　号',
                  fill='#ffffff',
                  font=font_t_jp,
                  stroke_width=0)
        draw.text(xy=(90, 570),
                  text='HONOR',
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1)
        # main
        for col, image in enumerate(honor_thumbnails):
            tmp.paste(im=image, box=((380 + 10) * col + 60, 730), mask=image)
            if honor_rarities[col] == 'middle':
                feather = Image.open(
                    os.path.join(os.path.dirname(__file__),
                                 'assets/frame/feather.png'))
                tmp.paste(im=feather,
                          box=((380 + 10) * col + 60, 730),
                          mask=feather)
            elif honor_rarities[col] == 'high':
                flower = Image.open(
                    os.path.join(os.path.dirname(__file__),
                                 'assets/frame/flower.png'))
                tmp.paste(im=flower,
                          box=((380 + 10) * col + 60, 730),
                          mask=flower)
            elif honor_rarities[col] == 'highest':
                flower_ring = Image.open(
                    os.path.join(os.path.dirname(__file__),
                                 'assets/frame/flower_ring.png'))
                tmp.paste(im=flower_ring,
                          box=((380 + 10) * col + 60, 730),
                          mask=flower_ring)
            else:
                pass
            if re.search('TOP', honor_names[col]) is not None:
                event_rank = honor_names[col].split('TOP')[1]
                event_rank = format(int(event_rank), '06d')
                top_fig = Image.open(
                    os.path.join(os.path.dirname(__file__),
                                 f'assets/frame/honor_top_{event_rank}.png'))
                tmp.paste(im=top_fig,
                          box=((380 + 10) * col + 250, 730),
                          mask=top_fig)


        # part 3 deck
        print('prepare deck')
        # title border
        draw.rounded_rectangle(xy=[62, 880, 1302, 960],
                               radius=20,
                               fill='#39c5bb',
                               outline=None,
                               width=3)
        draw.text(xy=(92, 840),
                  text='DECK MEMBER',
                  fill='#39c5bb',
                  font=font_t_en,
                  stroke_width=1)
        # title
        draw.rounded_rectangle(xy=[60, 880, 1300, 960],
                               radius=20,
                               fill='#444466',
                               outline=None,
                               width=3)
        draw.text(xy=(90, 895),
                  text='デック　メンバー',
                  fill='#ffffff',
                  font=font_t_jp,
                  stroke_width=0)
        draw.text(xy=(90, 840),
                  text='DECK MEMBER',
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1)
        # main
        for idx, img in enumerate(deck_images):
            frame = Image.open(
                os.path.join(os.path.dirname(__file__),
                             f'assets/frame/cardFrame_{deck_frame_ids[idx]}.png')).resize(
                                 (220, 440), Image.ANTIALIAS)
            img = img.crop((163, 0, 438, 550)).resize((220, 440),
                                                      Image.ANTIALIAS)
            tmp.paste(im=img, box=((220 + 25) * idx + 80, 1000), mask=img)
            tmp.paste(im=frame, box=((220 + 25) * idx + 80, 1000), mask=frame)

        # part 4 challenge
        print('prepare challenge')
        # title border
        draw.rounded_rectangle(xy=[1362, 100, 2102, 180],
                               radius=20,
                               fill='#39c5bb',
                               outline=None,
                               width=3)
        draw.text(xy=(1392, 60),
                  text='CHALLENGE LIVE',
                  fill='#39c5bb',
                  font=font_t_en,
                  stroke_width=1)
        # title
        draw.rounded_rectangle(xy=[1360, 100, 2100, 180],
                               radius=20,
                               fill='#444466',
                               outline=None,
                               width=3)
        draw.text(xy=(1390, 115),
                  text='チャレンジ　ライブ',
                  fill='#ffffff',
                  font=font_t_jp,
                  stroke_width=0)
        draw.text(xy=(1390, 60),
                  text='CHALLENGE LIVE',
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1)
        # main
        if challange_result[0]['characterId'] < 21:
            chr_tl = Image.open(
                os.path.join(
                    os.path.dirname(__file__),
                    f"assets/character/chr_tl/chr_tl_{challange_result[0]['characterId']}.png"
                )).resize((207, 407), Image.ANTIALIAS)
            tmp.paste(chr_tl, (1390, 220), mask=chr_tl)
            draw.rounded_rectangle(xy=[1390, 220, 1597, 627],
                                   radius=10,
                                   fill=None,
                                   outline='#e6e6e6',
                                   width=3)
        else:
            chr_tl = Image.open(
                os.path.join(
                    os.path.dirname(__file__),
                    f"assets/character/chr_tl/chr_tl_{challange_result[0]['characterId']}.png"
                )).resize((158, 407), Image.ANTIALIAS)
            tmp.paste(chr_tl, (1415, 220), mask=chr_tl)
            draw.rounded_rectangle(xy=[1415, 220, 1573, 627],
                                   radius=10,
                                   fill=None,
                                   outline='#e6e6e6',
                                   width=3)
        draw.rounded_rectangle(xy=[1630, 220, 2060, 627],
                               radius=20,
                               fill='#ffffe0',
                               outline='#e6e6e6',
                               width=3)
        draw.rounded_rectangle(xy=[1670, 260, 2020, 320],
                               radius=30,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3)
        draw.text(xy=(1730, 275),
                  text='HIGH SCORE',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1)
        draw.text(xy=(1730, 335),
                  text=str(challange_result[0]['highScore']),
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1)
        draw.rounded_rectangle(xy=[1650, 400, 2040, 460],
                               radius=30,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3)
        draw.text(xy=(1690, 415),
                  text='CHALLENGE RANK',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1)
        chara_circ = Image.open(
            os.path.join(
                os.path.dirname(__file__),
                f'assets/character/chr_ts/chr_ts_{best_rank_id + 1}.png'))
        tmp.paste(chara_circ, (1690, 470), mask=chara_circ)
        draw.rounded_rectangle(xy=[1870, 472, 1992, 600],
                               radius=64,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=4)
        draw.rounded_rectangle(xy=[1874, 478, 1988, 594],
                               radius=56,
                               fill='#ffffff',
                               outline='#39c5bb',
                               width=4)
        draw.text(xy=(1932, 556),
                  text=str(max(challange_ranks)),
                  fill='#444466',
                  font=font_t_en,
                  anchor='ms',
                  align='center',
                  stroke_width=1)

        # part 5 chara
        print('prepare chara')
        # title border
        draw.rounded_rectangle(xy=[1362, 700, 2102, 780],
                               radius=20,
                               fill='#39c5bb',
                               outline=None,
                               width=3)
        draw.text(xy=(1392, 660),
                  text='CHARACTER RANK',
                  fill='#39c5bb',
                  font=font_t_en,
                  stroke_width=1)
        # title
        draw.rounded_rectangle(xy=[1360, 700, 2100, 780],
                               radius=20,
                               fill='#444466',
                               outline=None,
                               width=3)
        draw.text(xy=(1390, 715),
                  text='キャラクター　ランク',
                  fill='#ffffff',
                  font=font_t_jp,
                  stroke_width=0)
        draw.text(xy=(1390, 660),
                  text='CHARACTER RANK',
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1)
        # main
        for row in range(6):
            for col in range(4):
                idx = row * 4 + col + 1
                chr_ts = Image.open(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/chr_ts/chr_ts_{idx}.png')).resize(
                            (100, 100), Image.ANTIALIAS)
                draw.rounded_rectangle(xy=[(100 + 80) * col + 1420,
                                           (100 + 10) * row + 860,
                                           (100 + 80) * col + 1540,
                                           (100 + 10) * row + 920],
                                       radius=30,
                                       fill='#ffffff',
                                       outline='#e6e6e6',
                                       width=5)
                draw.rounded_rectangle(xy=[(100 + 80) * col + 1420,
                                           (100 + 10) * row + 860,
                                           (100 + 80) * col + 1540,
                                           (100 + 10) * row + 920],
                                       radius=30,
                                       fill='#ffffff',
                                       outline='#39c5bb',
                                       width=3)
                tmp.paste(im=chr_ts,
                          box=((100 + 80) * col + 1380,
                               (100 + 10) * row + 820),
                          mask=chr_ts)
                draw.text(xy=((100 + 80) * col + 1505, (100 + 10) * row + 905),
                          text=str(chara_ranks[idx - 1]),
                          fill='#444466',
                          font=font_c_jp,
                          anchor='ms',
                          align='center',
                          stroke_width=1)
        for idx in range(25, 27):
            row = 6
            col = idx - 25
            chr_ts = Image.open(
                os.path.join(
                    os.path.dirname(__file__),
                    f'assets/character/chr_ts/chr_ts_{idx}.png')).resize(
                        (100, 100), Image.ANTIALIAS)
            draw.rounded_rectangle(xy=[(100 + 80) * col + 1420,
                                       (100 + 10) * row + 860,
                                       (100 + 80) * col + 1540,
                                       (100 + 10) * row + 920],
                                   radius=30,
                                   fill='#ffffff',
                                   outline='#e6e6e6',
                                   width=5)
            draw.rounded_rectangle(xy=[(100 + 80) * col + 1420,
                                       (100 + 10) * row + 860,
                                       (100 + 80) * col + 1540,
                                       (100 + 10) * row + 920],
                                   radius=30,
                                   fill='#ffffff',
                                   outline='#39c5bb',
                                   width=3)
            tmp.paste(im=chr_ts,
                      box=((100 + 80) * col + 1380, (100 + 10) * row + 820),
                      mask=chr_ts)
            draw.text(xy=((100 + 80) * col + 1505, (100 + 10) * row + 905),
                      text=str(chara_ranks[idx - 1]),
                      fill='#444466',
                      font=font_c_jp,
                      anchor='ms',
                      align='center',
                      stroke_width=1)

        # part 6 music
        print('prepare music')
        # title border
        draw.rounded_rectangle(xy=[62, 1505, 1302, 1585],
                               radius=20,
                               fill='#39c5bb',
                               outline=None,
                               width=3)
        draw.text(xy=(92, 1465),
                  text='LIVE STATUS',
                  fill='#39c5bb',
                  font=font_t_en,
                  stroke_width=1)
        # title
        draw.rounded_rectangle(xy=[60, 1505, 1300, 1585],
                               radius=20,
                               fill='#444466',
                               outline=None,
                               width=3)
        draw.text(xy=(90, 1520),
                  text='ライブ　ステータス',
                  fill='#ffffff',
                  font=font_t_jp,
                  stroke_width=0)
        draw.text(xy=(90, 1465),
                  text='LIVE STATUS',
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1)
        # main みなに伝えたい想い
        draw.rounded_rectangle(xy=[80, 1620, 1280, 1880],
                               radius=20,
                               fill=None,
                               outline='#e6e6e6',
                               width=3)
        draw.rounded_rectangle(xy=[80, 1620, 1280, 1880],
                               radius=20,
                               fill='#ffffe0',
                               outline='#e6e6e6',
                               width=3)
        draw.rounded_rectangle(xy=[100, 1640, 360, 1700],
                               radius=30,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3)
        draw.rounded_rectangle(xy=[100, 1720, 360, 1780],
                               radius=30,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3)
        draw.rounded_rectangle(xy=[100, 1800, 360, 1860],
                               radius=30,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3)
        draw.text(xy=(170, 1655),
                  text='CLEAR',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1)
        draw.text(xy=(122, 1735),
                  text='FULL COMBO',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1)
        draw.text(xy=(120, 1815),
                  text='ALL PERFECT',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1)
        palette_diff = ['#67dc11', '#33bbed', '#ffaa00', '#ee4566', '#bb33ef']
        for row in range(3):
            for col in range(5):
                draw.rounded_rectangle(xy=[(110 + 60) * col + 400,
                                           (60 + 20) * row + 1640,
                                           (110 + 60) * col + 540,
                                           (60 + 20) * row + 1700],
                                       radius=20,
                                       fill=palette_diff[col],
                                       outline='#e6e6e6',
                                       width=0)
                draw.text(xy=((110 + 60) * col + 470, (60 + 20) * row + 1684),
                          text=str(music_status[row][col]),
                          fill='#ffffff',
                          font=font_c_jp,
                          anchor='ms',
                          align='center',
                          stroke_width=1)

        # part 7 post script
        print('prepare ps')
        # main
        draw.rounded_rectangle(xy=[1440, 1620, 2060, 1850],
                               radius=20,
                               fill='#ffffff',
                               outline='#e6e6e6',
                               width=3)
        lines = textwrap.wrap(word, width=17)
        y_text = 1620
        width, height = font_c_jp.getsize(word)
        for idx, line in enumerate(lines):
            draw.text((1460, 1640 + (height + 2) * idx),
                      line,
                      font=font_c_jp,
                      fill='#444466')
            y_text += height
        tmp.save('/home/phynon/opt/cqhttp/data/images/tmp_result.png')
        profile_result = '[CQ:image,file=tmp_result.png]'
        # tmp.convert('RGB').save('/home/phynon/opt/cqhttp/data/images/tmp_result.jpg')
        # profile_result = '[CQ:image,file=tmp_result.jpg]'
        print(profile_result)
        await session.send(profile_result)
    except _FinishException as identifier:
        pass
    except Exception as identifier:
        print(repr(identifier))
        print(identifier)
        await session.send('通信エラー：接続ができません')
    else:
        pass

@myprofile.args_parser
async def _(session: CommandSession):
    players_dir = os.path.join(os.path.dirname(__file__),
                               '../metas/known_players.json')
    with open(players_dir, 'r') as f:
        if f.read(1):
            f.seek(0, 0)
            players = json.load(f)
        else:
            players = {}
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
            session.finish('セカイへようこそ！\n' + '初次见面，请发送\n' + '"myrank 好友码"\n' +
                           '来告诉您的信息！')
    session.state[session.current_key] = stripped_arg


def concat_images(images, path):
    target = Image.new('RGB', (380 * 3 + 20, 100), '#e6e6e6')
    for col in range(3):
        target.paste(images[col], ((380 + 10) * col, 10), mask=images[col])
    target.save(path)
    return


@on_command('mysongs', aliases=['查歌'], only_to_me=False)
async def mysongs(session):
    try:
        src = 'http://127.0.0.1:5000/profile'
        uid = session.get('uid')
        rq = {'uid': uid}
        print(rq)
        response = requests.post(src, rq)
        print(response.content)
        data = json.loads(response.content)
        data = data['userProfile']['word']
        ranking = data
        await session.send(ranking)
    except Exception as identifier:
        print(identifier)
        await session.send(identifier)
    else:
        pass


@mysongs.args_parser
async def _(session: CommandSession):
    players_dir = os.path.join(os.path.dirname(__file__),
                               '../metas/known_players.json')
    with open(players_dir, 'r') as f:
        if f.read(1):
            f.seek(0, 0)
            players = json.load(f)
        else:
            players = {}
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
        session.finish('セカイへようこそ！\n' + '初次见面，请发送\n' + '"myrank 好友码"\n' +
                       '来告诉您的信息！')
    if session.is_first_run:
        if stripped_arg:
            if flag:
                print(flag)
                session.state['uid'] = players[user_qq]
