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

    print(profile_honor)

    honor_thumbnails = []
    for i in range(3):
        image = Image.new('RGBA', [1, 1])
        honor_thumbnails.append(image)
    honor_names = ['', '', '']
    honor_rarities = ['', '', '']

    for honor in profile_honor:
        if honor['profileHonorType'] == 'bond':
            pass
        elif honor['profileHonorType'] == 'normal':
            honor_id = honor['honorId']
            seq = honor['seq'] - 1
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
            honor_thumbnails[seq] = image
            honor_names[seq] = honor_metas[int(honor_id)]['name']
            honor_rarities[seq] = honor_metas[int(honor_id)]['honorRarity']

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
        bg_list = [
            '01_01', '01_02', '02_01', '02_02', '03_01', '03_02', '04_01',
            '04_02', '05_01', '05_02', '06_01', '06_02'
        ]
        honor_coro = prepare_honor_images(data['userProfileHonors'])
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
        tmp = tmp.resize((2160 * 2, 1920 * 2), resample=Image.LANCZOS)
        word = profile['word']
        font_t_jp = ImageFont.truetype(
            os.path.join(os.path.dirname(__file__),
                         'assets/fonts/BIZ-UDPGothicB.ttf'), 50 * 2)
        font_t_en = ImageFont.truetype(
            os.path.join(os.path.dirname(__file__),
                         'assets/fonts/BIZ-UDPGothicB.ttf'), 45 * 2)
        font_t2_en = ImageFont.truetype(
            os.path.join(os.path.dirname(__file__),
                         'assets/fonts/BIZ-UDPGothicB.ttf'), 30 * 2)
        font_c_jp = ImageFont.truetype(
            os.path.join(os.path.dirname(__file__),
                         'assets/fonts/BIZ-UDPGothicB.ttf'), 35 * 2)
        font_c_en = ImageFont.truetype(
            os.path.join(os.path.dirname(__file__),
                         'assets/fonts/BIZ-UDPGothicB.ttf'), 26 * 2)
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
        draw.rounded_rectangle(xy=[62 * 2, 100 * 2, 1302 * 2, 180 * 2],
                               radius=20 * 2,
                               fill='#39c5bb',
                               outline=None,
                               width=3 * 2)
        draw.text(xy=(92 * 2, 60 * 2),
                  text='PROFILE',
                  fill='#39c5bb',
                  font=font_t_en,
                  stroke_width=1 * 2)
        # title
        draw.rounded_rectangle(xy=[60 * 2, 100 * 2, 1300 * 2, 180 * 2],
                               radius=20 * 2,
                               fill='#444466',
                               outline=None,
                               width=3 * 2)
        draw.text(xy=(90 * 2, 115 * 2),
                  text='プロファイル',
                  fill='#ffffff',
                  font=font_t_jp,
                  stroke_width=0)
        draw.text(xy=(90 * 2, 60 * 2),
                  text='PROFILE',
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1 * 2)
        # main
        leader = leader[0].resize((600 * 2, 338 * 2), Image.LANCZOS)
        # print(leader.size)
        mask = Image.new('RGBA', (600 * 2, 338 * 2))
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle(xy=[0, 0, 600 * 2, 338 * 2],
                                    radius=15 * 2,
                                    fill='#ffffe0',
                                    outline='#e6e6e6',
                                    width=3 * 2)
        tmp.paste(im=leader, box=(80 * 2, 210 * 2), mask=mask)
        draw.rounded_rectangle(xy=[80 * 2, 210 * 2, 680 * 2, 548 * 2],
                               radius=15 * 2,
                               fill=None,
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.rounded_rectangle(xy=[720 * 2, 210 * 2, 1280 * 2, 548 * 2],
                               radius=20 * 2,
                               fill='#ffffe0',
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.rounded_rectangle(xy=[740 * 2, 229 * 2, 920 * 2, 289 * 2],
                               radius=30 * 2,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.rounded_rectangle(xy=[740 * 2, 309 * 2, 920 * 2, 369 * 2],
                               radius=30 * 2,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.rounded_rectangle(xy=[740 * 2, 389 * 2, 920 * 2, 449 * 2],
                               radius=30 * 2,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.rounded_rectangle(xy=[740 * 2, 469 * 2, 920 * 2, 529 * 2],
                               radius=30 * 2,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.text(xy=(780 * 2, 245 * 2),
                  text='NAME',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1 * 2)
        draw.text(xy=(798 * 2, 325 * 2),
                  text='UID',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1 * 2)
        draw.text(xy=(780 * 2, 405 * 2),
                  text='RANK',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1 * 2)
        draw.text(xy=(755 * 2, 485 * 2),
                  text='TWITTER',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1 * 2)
        draw.text(xy=(940 * 2, 240 * 2),
                  text=data['user']['userGamedata']['name'],
                  fill='#444466',
                  font=font_c_jp,
                  stroke_width=1 * 2)
        draw.text(xy=(940 * 2, 327 * 2),
                  text=str(data['user']['userGamedata']['userId']),
                  fill='#444466',
                  font=font_c_en,
                  stroke_width=1 * 2)
        draw.text(xy=(940 * 2, 400 * 2),
                  text=str(data['user']['userGamedata']['rank']),
                  fill='#444466',
                  font=font_c_jp,
                  stroke_width=1 * 2)
        draw.text(xy=(940 * 2, 480 * 2),
                  text=data['userProfile']['twitterId'],
                  fill='#444466',
                  font=font_c_jp,
                  stroke_width=1 * 2)
        # part 2 honorI
        print('prepare honor')
        # title border
        draw.rounded_rectangle(xy=[62 * 2, 610 * 2, 1302 * 2, 690 * 2],
                               radius=20 * 2,
                               fill='#39c5bb',
                               outline=None,
                               width=3 * 2)
        draw.text(xy=(92 * 2, 570 * 2),
                  text='HONOR',
                  fill='#39c5bb',
                  font=font_t_en,
                  stroke_width=1 * 2)
        # title
        draw.rounded_rectangle(xy=[60 * 2, 610 * 2, 1300 * 2, 690 * 2],
                               radius=20 * 2,
                               fill='#444466',
                               outline=None,
                               width=3 * 2)
        draw.text(xy=(90 * 2, 625 * 2),
                  text='称　号',
                  fill='#ffffff',
                  font=font_t_jp,
                  stroke_width=0)
        draw.text(xy=(90 * 2, 570 * 2),
                  text='HONOR',
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1 * 2)
        # main
        for col, image in enumerate(honor_thumbnails):
            image = image.resize((380 * 2, 80 * 2), Image.LANCZOS)
            tmp.paste(im=image, box=(((380 + 10) * col + 60) * 2, 730 * 2), mask=image)
            print(honor_thumbnails[col].size)
            if honor_rarities[col] == 'middle':
                feather = Image.open(
                    os.path.join(os.path.dirname(__file__),
                                 'assets/frame/feather.png')).resize((380 * 2, 80 * 2), Image.LANCZOS)
                tmp.paste(im=feather,
                          box=(((380 + 10) * col + 60) * 2, 730 * 2),
                          mask=feather)
            elif honor_rarities[col] == 'high':
                flower = Image.open(
                    os.path.join(os.path.dirname(__file__),
                                 'assets/frame/flower.png')).resize((380 * 2, 80 * 2), Image.LANCZOS)
                tmp.paste(im=flower,
                          box=(((380 + 10) * col + 60) * 2, 730 * 2),
                          mask=flower)
            elif honor_rarities[col] == 'highest':
                flower_ring = Image.open(
                    os.path.join(os.path.dirname(__file__),
                                 'assets/frame/flower_ring.png')).resize((380 * 2, 80 * 2), Image.LANCZOS)
                tmp.paste(im=flower_ring,
                          box=(((380 + 10) * col + 60) * 2, 730 * 2),
                          mask=flower_ring)
            else:
                pass
            if re.search('TOP', honor_names[col]) is not None:
                event_rank = honor_names[col].split('TOP')[1]
                event_rank = format(int(event_rank), '06d')
                top_fig = Image.open(
                    os.path.join(os.path.dirname(__file__),
                                 f'assets/frame/honor_top_{event_rank}.png')).resize((150 * 2, 78 * 2), Image.LANCZOS)
                tmp.paste(im=top_fig,
                          box=(((380 + 10) * col + 250) * 2, 730 * 2),
                          mask=top_fig)

        # part 3 deck
        print('prepare deck')
        # title border
        draw.rounded_rectangle(xy=[62 * 2, 880 * 2, 1302 * 2, 960 * 2],
                               radius=20 * 2,
                               fill='#39c5bb',
                               outline=None,
                               width=3 * 2)
        draw.text(xy=(92 * 2, 840 * 2),
                  text='DECK MEMBER',
                  fill='#39c5bb',
                  font=font_t_en,
                  stroke_width=1 * 2)
        # title
        draw.rounded_rectangle(xy=[60 * 2, 880 * 2, 1300 * 2, 960 * 2],
                               radius=20 * 2,
                               fill='#444466',
                               outline=None,
                               width=3 * 2)
        draw.text(xy=(90 * 2, 895 * 2),
                  text='デック　メンバー',
                  fill='#ffffff',
                  font=font_t_jp,
                  stroke_width=0)
        draw.text(xy=(90 * 2, 840 * 2),
                  text='DECK MEMBER',
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1 * 2)
        # main
        for idx, img in enumerate(deck_images):
            frame = Image.open(
                os.path.join(os.path.dirname(__file__),
                             f'assets/frame/cardFrame_{deck_frame_ids[idx]}.png')).resize(
                (220 * 2, 440 * 2), Image.LANCZOS)
            img = img.crop((163, 0, 438, 550)).resize((220 * 2, 440 * 2),
                                                      Image.LANCZOS)
            tmp.paste(im=img, box=(((220 + 25) * idx + 80) * 2, 1000 * 2), mask=img)
            tmp.paste(im=frame, box=(((220 + 25) * idx + 80) * 2, 1000 * 2), mask=frame)

        # part 4 challenge
        print('prepare challenge')
        # title border
        draw.rounded_rectangle(xy=[1362 * 2, 100 * 2, 2102 * 2, 180 * 2],
                               radius=20 * 2,
                               fill='#39c5bb',
                               outline=None,
                               width=3 * 2)
        draw.text(xy=(1392 * 2, 60 * 2),
                  text='CHALLENGE LIVE',
                  fill='#39c5bb',
                  font=font_t_en,
                  stroke_width=1 * 2)
        # title
        draw.rounded_rectangle(xy=[1360 * 2, 100 * 2, 2100 * 2, 180 * 2],
                               radius=20 * 2,
                               fill='#444466',
                               outline=None,
                               width=3 * 2)
        draw.text(xy=(1390 * 2, 115 * 2),
                  text='チャレンジ　ライブ',
                  fill='#ffffff',
                  font=font_t_jp,
                  stroke_width=0)
        draw.text(xy=(1390 * 2, 60 * 2),
                  text='CHALLENGE LIVE',
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1 * 2)
        # main
        if challange_result[0]['characterId'] < 21:
            chr_tl = Image.open(
                os.path.join(
                    os.path.dirname(__file__),
                    f"assets/character/chr_tl/chr_tl_{challange_result[0]['characterId']}.png"
                )).resize((207 * 2, 407 * 2), Image.LANCZOS)
            tmp.paste(chr_tl, (1390 * 2, 220 * 2), mask=chr_tl)
            draw.rounded_rectangle(xy=[1390 * 2, 220 * 2, 1597 * 2, 627 * 2],
                                   radius=10 * 2,
                                   fill=None,
                                   outline='#e6e6e6',
                                   width=3 * 2)
        else:
            chr_tl = Image.open(
                os.path.join(
                    os.path.dirname(__file__),
                    f"assets/character/chr_tl/chr_tl_{challange_result[0]['characterId']}.png"
                )).resize((158 * 2, 407 * 2), Image.LANCZOS)
            tmp.paste(chr_tl, (1415 * 2, 220 * 2), mask=chr_tl)
            draw.rounded_rectangle(xy=[1415 * 2, 220 * 2, 1573 * 2, 627 * 2],
                                   radius=10 * 2,
                                   fill=None,
                                   outline='#e6e6e6',
                                   width=3 * 2)
        draw.rounded_rectangle(xy=[1630 * 2, 220 * 2, 2060 * 2, 627 * 2],
                               radius=20 * 2,
                               fill='#ffffe0',
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.rounded_rectangle(xy=[1670 * 2, 260 * 2, 2020 * 2, 320 * 2],
                               radius=30 * 2,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.text(xy=(1730 * 2, 275 * 2),
                  text='HIGH SCORE',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1 * 2)
        draw.text(xy=(1730 * 2, 335 * 2),
                  text=str(challange_result[0]['highScore']),
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1 * 2)
        draw.rounded_rectangle(xy=[1650 * 2, 400 * 2, 2040 * 2, 460 * 2],
                               radius=30 * 2,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.text(xy=(1690 * 2, 415 * 2),
                  text='CHALLENGE RANK',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1 * 2)
        chara_circ = Image.open(
            os.path.join(
                os.path.dirname(__file__),
                f'assets/character/chr_ts/chr_ts_{best_rank_id + 1}.png')).resize((128 * 2, 128 * 2), Image.LANCZOS)
        tmp.paste(chara_circ, (1690 * 2, 470 * 2), mask=chara_circ)
        draw.rounded_rectangle(xy=[1870 * 2, 472 * 2, 1992 * 2, 600 * 2],
                               radius=64 * 2,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=4 * 2)
        draw.rounded_rectangle(xy=[1874 * 2, 478 * 2, 1988 * 2, 594 * 2],
                               radius=56 * 2,
                               fill='#ffffff',
                               outline='#39c5bb',
                               width=4 * 2)
        draw.text(xy=(1932 * 2, 556 * 2),
                  text=str(max(challange_ranks)),
                  fill='#444466',
                  font=font_t_en,
                  anchor='ms',
                  align='center',
                  stroke_width=1 * 2)

        # part 5 chara
        print('prepare chara')
        # title border
        draw.rounded_rectangle(xy=[1362 * 2, 700 * 2, 2102 * 2, 780 * 2],
                               radius=20 * 2,
                               fill='#39c5bb',
                               outline=None,
                               width=3 * 2)
        draw.text(xy=(1392 * 2, 660 * 2),
                  text='CHARACTER RANK',
                  fill='#39c5bb',
                  font=font_t_en,
                  stroke_width=1 * 2)
        # title
        draw.rounded_rectangle(xy=[1360 * 2, 700 * 2, 2100 * 2, 780 * 2],
                               radius=20 * 2,
                               fill='#444466',
                               outline=None,
                               width=3 * 2)
        draw.text(xy=(1390 * 2, 715 * 2),
                  text='キャラクター　ランク',
                  fill='#ffffff',
                  font=font_t_jp,
                  stroke_width=0)
        draw.text(xy=(1390 * 2, 660 * 2),
                  text='CHARACTER RANK',
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1 * 2)
        # main
        for row in range(6):
            for col in range(4):
                idx = row * 4 + col + 1
                chr_ts = Image.open(
                    os.path.join(
                        os.path.dirname(__file__),
                        f'assets/character/chr_ts/chr_ts_{idx}.png')).resize(
                    (100 * 2, 100 * 2), Image.LANCZOS)
                draw.rounded_rectangle(xy=[((100 + 80) * col + 1420) * 2,
                                           ((100 + 10) * row + 860) * 2,
                                           ((100 + 80) * col + 1540) * 2,
                                           ((100 + 10) * row + 920) * 2],
                                       radius=30 * 2,
                                       fill='#ffffff',
                                       outline='#e6e6e6',
                                       width=5 * 2)
                draw.rounded_rectangle(xy=[((100 + 80) * col + 1420) * 2,
                                           ((100 + 10) * row + 860) * 2,
                                           ((100 + 80) * col + 1540) * 2,
                                           ((100 + 10) * row + 920) * 2],
                                       radius=30 * 2,
                                       fill='#ffffff',
                                       outline='#39c5bb',
                                       width=3 * 2)
                tmp.paste(im=chr_ts,
                          box=(((100 + 80) * col + 1380) * 2,
                               ((100 + 10) * row + 820) * 2),
                          mask=chr_ts)
                draw.text(xy=(((100 + 80) * col + 1505) * 2, ((100 + 10) * row + 905) * 2),
                          text=str(chara_ranks[idx - 1]),
                          fill='#444466',
                          font=font_c_jp,
                          anchor='ms',
                          align='center',
                          stroke_width=1 * 2)
        for idx in range(25, 27):
            row = 6
            col = idx - 25
            chr_ts = Image.open(
                os.path.join(
                    os.path.dirname(__file__),
                    f'assets/character/chr_ts/chr_ts_{idx}.png')).resize(
                (100 * 2, 100 * 2), Image.LANCZOS)
            draw.rounded_rectangle(xy=[((100 + 80) * col + 1420) * 2,
                                       ((100 + 10) * row + 860) * 2,
                                       ((100 + 80) * col + 1540) * 2,
                                       ((100 + 10) * row + 920) * 2],
                                   radius=30 * 2,
                                   fill='#ffffff',
                                   outline='#e6e6e6',
                                   width=5 * 2)
            draw.rounded_rectangle(xy=[((100 + 80) * col + 1420) * 2,
                                       ((100 + 10) * row + 860) * 2,
                                       ((100 + 80) * col + 1540) * 2,
                                       ((100 + 10) * row + 920) * 2],
                                   radius=30 * 2,
                                   fill='#ffffff',
                                   outline='#39c5bb',
                                   width=3 * 2)
            tmp.paste(im=chr_ts,
                      box=(((100 + 80) * col + 1380) * 2, ((100 + 10) * row + 820) * 2),
                      mask=chr_ts)
            draw.text(xy=(((100 + 80) * col + 1505) * 2, ((100 + 10) * row + 905) * 2),
                      text=str(chara_ranks[idx - 1]),
                      fill='#444466',
                      font=font_c_jp,
                      anchor='ms',
                      align='center',
                      stroke_width=1 * 2)

        # part 6 music
        print('prepare music')
        # title border
        draw.rounded_rectangle(xy=[62 * 2, 1505 * 2, 1302 * 2, 1585 * 2],
                               radius=20 * 2,
                               fill='#39c5bb',
                               outline=None,
                               width=3 * 2)
        draw.text(xy=(92 * 2, 1465 * 2),
                  text='LIVE STATUS',
                  fill='#39c5bb',
                  font=font_t_en,
                  stroke_width=1 * 2)
        # title
        draw.rounded_rectangle(xy=[60 * 2, 1505 * 2, 1300 * 2, 1585 * 2],
                               radius=20 * 2,
                               fill='#444466',
                               outline=None,
                               width=3 * 2)
        draw.text(xy=(90 * 2, 1520 * 2),
                  text='ライブ　ステータス',
                  fill='#ffffff',
                  font=font_t_jp,
                  stroke_width=0)
        draw.text(xy=(90 * 2, 1465 * 2),
                  text='LIVE STATUS',
                  fill='#444466',
                  font=font_t_en,
                  stroke_width=1 * 2)
        # main みなに伝えたい想い
        draw.rounded_rectangle(xy=[80 * 2, 1620 * 2, 1280 * 2, 1880 * 2],
                               radius=20 * 2,
                               fill=None,
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.rounded_rectangle(xy=[80 * 2, 1620 * 2, 1280 * 2, 1880 * 2],
                               radius=20 * 2,
                               fill='#ffffe0',
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.rounded_rectangle(xy=[100 * 2, 1640 * 2, 360 * 2, 1700 * 2],
                               radius=30 * 2,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.rounded_rectangle(xy=[100 * 2, 1720 * 2, 360 * 2, 1780 * 2],
                               radius=30 * 2,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.rounded_rectangle(xy=[100 * 2, 1800 * 2, 360 * 2, 1860 * 2],
                               radius=30 * 2,
                               fill='#39c5bb',
                               outline='#e6e6e6',
                               width=3 * 2)
        draw.text(xy=(170 * 2, 1655 * 2),
                  text='CLEAR',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1 * 2)
        draw.text(xy=(122 * 2, 1735 * 2),
                  text='FULL COMBO',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1 * 2)
        draw.text(xy=(120 * 2, 1815 * 2),
                  text='ALL PERFECT',
                  fill='#ffffff',
                  font=font_t2_en,
                  stroke_width=1 * 2)
        palette_diff = ['#67dc11', '#33bbed', '#ffaa00', '#ee4566', '#bb33ef']
        for row in range(3):
            for col in range(5):
                draw.rounded_rectangle(xy=[((110 + 60) * col + 400) * 2,
                                           ((60 + 20) * row + 1640) * 2,
                                           ((110 + 60) * col + 540) * 2,
                                           ((60 + 20) * row + 1700) * 2],
                                       radius=20 * 2,
                                       fill=palette_diff[col],
                                       outline='#e6e6e6',
                                       width=0)
                draw.text(xy=(((110 + 60) * col + 470) * 2, ((60 + 20) * row + 1684) * 2),
                          text=str(music_status[row][col]),
                          fill='#ffffff',
                          font=font_c_jp,
                          anchor='ms',
                          align='center',
                          stroke_width=1 * 2)

        # part 7 post script
        print('prepare ps')
        # main
        draw.rounded_rectangle(xy=[1440 * 2, 1620 * 2, 2060 * 2, 1850 * 2],
                               radius=20 * 2,
                               fill='#ffffff',
                               outline='#e6e6e6',
                               width=3 * 2)
        lines = textwrap.wrap(word, width=17 * 2)
        y_text = 1620 * 2
        width, height = font_c_jp.getsize(word)
        for idx, line in enumerate(lines):
            draw.text((1460 * 2, (1640 + (height + 2) * idx) * 2),
                      line,
                      font=font_c_jp,
                      fill='#444466')
            y_text += height
        tmp = tmp.resize((2160, 1920), resample=Image.ANTIALIAS)
        tmp.save('/home/phynon/opt/cqhttp/data/images/tmp_result.png')
        profile_result = '[CQ:image,file=tmp_result.png]'
        # tmp.convert('RGB').save('/home/phynon/opt/cqhttp/data/images/tmp_result.jpg')
        # profile_result = '[CQ:image,file=tmp_result.jpg]'
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
