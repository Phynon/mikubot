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
import nonebot
from miku.modules.sekaiutils import check_local_card_asset
from miku.modules.sekaiutils import get_card_thb
from miku.modules.sekaiutils import headers_sekaiviewer
from miku.modules.sekaiutils import audio_update_assets
from miku.modules.sekaiutils import audio_update_aliases
from miku.modules.sekaiutils import audio_update_list

headers_pjsekai = {
    'DNT': '1',
    'Referer': 'https://pjsek.ai/',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

@nonebot.scheduler.scheduled_job(
    'cron',
    # year=None,
    # month=None,
    # day=None,
    # week=None,
    # day_of_week=None,
    hour='14',
    minute='5',
    # second=None,
    # start_date=None,
    # end_date=None,
    # timezone=None,
)
async def card_resources_scheduler():
    bot = nonebot.get_bot()
    try:
        time.sleep(random.randint(1, 20))
        url = 'https://sekai-world.github.io/sekai-master-db-diff/cards.json'
        raw_data = requests.get(url, headers=headers_sekaiviewer)
        data = json.loads(raw_data.content)
        cards_list_dir = os.path.join(os.path.dirname(__file__), '../metas/cards_list.json')
        with open(cards_list_dir, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        await bot.send_group_msg(group_id=773737472, message=f"sekai中已有{len(list(data))}张卡牌。\n你今天想要谁的陪伴呢？")
        time.sleep(100 + random.randint(1, 80))
        for item in data:
            asset_name = item['assetbundleName']
            if item['cardRarityType'] in ('rarity_1', 'rarity_2', 'rarity_birthday'):
                after_should_exist = 0
                asset_exist_normal = check_local_thb_asset(asset_name, 'normal')
            else:
                after_should_exist = 1
                asset_exist_normal = check_local_thb_asset(asset_name, 'normal')
                asset_exist_after_training = check_local_thb_asset(asset_name, 'after_training')
            if not asset_exist_normal:
                get_card_thb(asset_name, 'normal')
            if after_should_exist and not asset_exist_after_training:
                get_card_thb(asset_name, 'after_training')
        await bot.send_group_msg(group_id=773737472, message="所有卡牌头图更新完成。")
    except Exception as identifier:
        print(identifier)

@nonebot.scheduler.scheduled_job(
    'cron',
    # year=None,
    # month=None,
    # day=None,
    # week=None,
    day_of_week='0,2,4,6',
    hour='18',
    minute='5',
    # second=None,
    # start_date=None,
    # end_date=None,
    # timezone=None,
)
async def song_resources_scheduler():
    bot = nonebot.get_bot()
    try:
        time.sleep(random.randint(1, 20))
        song_list, asset_list = audio_update_list()
        get_song_info = (f"sekai中现在有{len(set(song_list))}首歌曲，\n"
                         f"有{len(asset_list)}段不一样的歌声。\n"
                         f"你今天想要听到谁的思念呢？")
        await bot.send_group_msg(group_id=773737472, message=get_song_info)
        time.sleep(100 + random.randint(1, 80))
        audio_update_assets(asset_list)
        await bot.send_group_msg(group_id=773737472, message='歌曲文件更新完成')
        time.sleep(100 + random.randint(1, 80))
        index_list = audio_update_aliases()
        get_titles_info = (f"sekai中现在有{len(index_list)}首歌曲。\n"
                           f"添加歌曲别名请艾特我发送：\n"
                           f"歌曲标题也叫歌曲别名")
        await bot.send_group_msg(group_id=773737472, message=get_titles_info)
    except Exception as identifier:
        print(identifier)
