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
from nonebot import CommandSession, on_command

headers_sekaiviewer = {
    'DNT': '1',
    'Referer': 'https://sekai.best/',
    'cache-control': 'max-age=0',
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
async def _():
    bot = nonebot.get_bot()

    # get cards list
    url = 'https://sekai-world.github.io/sekai-master-db-diff/gachas.json'
    raw_data = requests.get(url, headers=headers_sekaiviewer)
    data = json.loads(raw_data.content)
    gacha_list_dir = os.path.join(os.path.dirname(__file__), 'gacha_list.json')
    with open(gacha_list_dir, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    get_gacha_info = (f"sekai中已有{len(list(data))}次招募卡池。\n你今天想要谁的陪伴呢？")
    await bot.send_group_msg(group_id=773737472, message=f"sekai中已有{len(list(data))}次招募卡池。\n你今天想要谁的陪伴呢？")
    time.sleep(100)
    # get cards thb
    url = 'https://sekai-world.github.io/sekai-master-db-diff/cards.json'
    raw_data = requests.get(url, headers=headers_sekaiviewer)
    data = json.loads(raw_data.content)
    cards_list_dir = os.path.join(os.path.dirname(__file__), 'cards_list.json')
    with open(cards_list_dir, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    get_cards_info = (f"sekai中已有{len(list(data))}张卡牌。\n你今天想要看到谁的故事呢？")
    await bot.send_group_msg(group_id=773737472, message=f"sekai中已有{len(list(data))}张卡牌。\n你今天想要看到谁的故事呢？")
    for item in data:
        asset_name = item['assetbundleName']
        chara_thumbnail_dir = os.path.join(os.path.dirname(__file__),
                                           f'../sekaiutils/thumbnail/chara/{asset_name}_normal.png')
        if not os.path.exists(os.path.join(os.path.dirname(__file__), '../sekaiutils/thumbnail/chara')):
            os.makedirs(os.path.join(os.path.dirname(__file__), '../sekaiutils/thumbnail/chara'))
        if os.path.exists(chara_thumbnail_dir):
            pass
        else:
            print(asset_name)
            url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/thumbnail/chara_rip/{asset_name}_normal.png'
            raw_data = requests.get(url)
            with open(chara_thumbnail_dir, 'wb') as f:
                f.write(raw_data.content)
    get_cards_thb = ("所有卡牌头图更新完成。")
    await bot.send_group_msg(group_id=773737472, message="所有卡牌头图更新完成。")

