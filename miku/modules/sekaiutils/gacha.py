import random
import requests
import json
import os
import shutil
from PIL import Image
from miku.utils import FreqLimiter
from nonebot import on_command, CommandSession
from miku.modules.sekaiutils import check_cooldown
from miku.modules.sekaiutils import check_local_card_asset
from miku.modules.sekaiutils import get_card_thb
from miku.modules.sekaiutils import check_local_gacha_banner
from miku.modules.sekaiutils import get_gacha_banner
from miku.modules.sekaiutils import gacha_load_metas
from miku.modules.sekaiutils import headers_sekaiviewer

limiter = FreqLimiter(10)


@on_command('gacha_ten',
            aliases='十连',
            only_to_me=True)
async def gacha_ten(session):
    if session.event['sender']['user_id'] is not None:
        user_qq = str(session.event['sender']['user_id'])
    else:
        user_qq = str(session.event['user_id'])
    await check_cooldown(session=session, user_qq=user_qq, limiter=limiter, time=7)
    gachas, master_data, cards = gacha_load_metas()
    on_gacha_idx = master_data['ongoing_gacha_id']
    for item in gachas:
        if item['id'] == on_gacha_idx:
            gacha = item
        else:
            pass
    gacha_indexes = []
    for item in gacha['gachaDetails']:
        gacha_indexes.append(item['cardId'])
    up_indexes = []
    for item in gacha['gachaPickups']:
        up_indexes.append(item['cardId'])
    for item in up_indexes:
        gacha_indexes.remove(item)
    gacha_cards = []
    for idx, card in enumerate(cards):
        if card['id'] in gacha_indexes:
            gacha_cards.append(card)
    up_cards = []
    for idx, card in enumerate(cards):
        if card['id'] in up_indexes:
            up_cards.append(card)
    rates = (int(gacha['rarity1Rate'] * 10),
             int(gacha['rarity2Rate'] * 10),
             int(gacha['rarity3Rate'] * 10),
             int(gacha['rarity4Rate'] * 10))
    up_rate = int(len(up_cards) * 4)
    result = []
    for idx in range(9):
        c = gacha_one(rates, up_rate, gacha_cards, up_cards)
        result.append(c)
    rates = (0,
             0,
             int((gacha['rarity3Rate'] + gacha['rarity4Rate']) * 10),
             int(gacha['rarity4Rate'] * 10))
    c = gacha_one(rates, up_rate, gacha_cards, up_cards)
    result.append(c)
    up_cnt = 0
    r4_cnt = 0
    r3_cnt = 0
    for card in result:
        if card['id'] in up_indexes:
            up_cnt += 1
        if card['rarity'] == 4:
            r4_cnt += 1
        if card['rarity'] == 3:
            r3_cnt += 1
    if up_cnt > 1:
        line = '要发红包要禁言（逗你玩的~）'
    elif up_cnt == 1 or r4_cnt > 1:
        line = '要发红包（逗你玩的~）'
    elif up_cnt == 0 and r4_cnt == 1:
        line = '不亏）'
    elif up_cnt == 0 and r4_cnt == 0 and r3_cnt > 1:
        line = '不亏（心虚）'
    else:
        line = '又保底了呢 呵呵~ 我还是转我的 反正不会变彩球'
    thumbnails = []
    for item in result:
        asset_name = item['assetbundleName']
        thumbnail_dir = os.path.join(os.path.dirname(__file__), f'thumbnail/chara/{asset_name}_normal.png')
        image = Image.open(thumbnail_dir)
        thumbnails.append(image)
    tmp_result_dir = '/home/phynon/opt/cqhttp/data/images/tmp_result.png'
    concat_images(thumbnails, tmp_result_dir)
    gacha_result = (f'[CQ:at,qq={user_qq}]\n'
                    f'当期up卡{up_cnt}张，4星卡{r4_cnt}张，3星卡{r3_cnt}张\n'
                    f'[CQ:image,file=tmp_result.png]\n'
                    f'{line}')
    print(gacha_result)
    await session.send(gacha_result)


def gacha_one(rates, up_rate, cards, up_cards):
    """
    rates: normal rates
    up_rate: total up card rates
    up_charas: up card info
    """
    r1_rate, r2_rate, r3_rate, r4_rate = rates
    total = sum(rates)
    r4_rate -= up_rate
    pick = random.randint(1, total)
    charas = []
    if pick <= up_rate:
        # up: uniform choice from up cards
        for idx, card in enumerate(up_cards):
            charas.append(card)
        return random.choice(charas)
    elif pick <= up_rate + r4_rate:
        # r4: uniform choice from other r4 cards
        for idx, card in enumerate(cards):
            if card['rarity'] == 4:
                charas.append(card)
        return random.choice(charas)
    elif pick <= up_rate + r4_rate + r3_rate:
        # r3
        for idx, card in enumerate(cards):
            if card['rarity'] == 3:
                charas.append(card)
        return random.choice(charas)
    elif pick <= up_rate + r4_rate + r3_rate + r2_rate:
        # r2
        for idx, card in enumerate(cards):
            if card['rarity'] == 2:
                charas.append(card)
        return random.choice(charas)
    else:
        # r1 impossible
        for idx, card in enumerate(cards):
            if card['rarity'] == 1:
                charas.append(card)
        return random.choice(charas)


def concat_images(images, path):
    target = Image.new('RGB', (128 * 5 + 20, 128 * 2 + 5), '#ffffff')
    for row in range(2):
        for col in range(5):
            target.paste(images[5 * row + col], ((128 + 5) * col, (128 + 5) * row))
    target.save(path)
    return


@on_command('get_gacha_list',
            aliases='更新卡池',
            only_to_me=False)
async def get_gacha_list(session):
    try:
        url = 'https://sekai-world.github.io/sekai-master-db-diff/gachas.json'
        raw_data = requests.get(url)
        data = json.loads(raw_data.content)
        gacha_list_dir = os.path.join(os.path.dirname(__file__), '../metas/gacha_list.json')
        with open(gacha_list_dir, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        get_gacha_info = (f"sekai中已有{len(list(data))}次招募卡池。\n"
                          f"你今天想要谁的陪伴呢？")
        await session.send(get_gacha_info)
    except Exception as identifier:
        print(identifier)


@on_command('get_cards_list',
            aliases='更新卡牌列表',
            only_to_me=False)
async def get_cards_list(session):
    try:
        url = 'https://sekai-world.github.io/sekai-master-db-diff/cards.json'
        raw_data = requests.get(url, headers=headers_sekaiviewer)
        data = json.loads(raw_data.content)
        cards_list_dir = os.path.join(os.path.dirname(__file__), '../metas/cards_list.json')
        with open(cards_list_dir, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        get_cards_info = (f"sekai中已有{len(list(data))}张卡牌。\n"
                          f"你今天想要看到谁的故事呢？")
        await session.send(get_cards_info)
        for item in data:
            asset_name = item['assetbundleName']
            asset_exist = check_local_card_asset(asset_name)
            if asset_exist:
                pass
            else:
                get_card_thb(asset_name)
        await session.send('所有卡牌头图更新完成。')
    except Exception as identifier:
        print(identifier)


@on_command('get_cards_thumbnails',
            aliases='更新卡牌头图',
            only_to_me=False)
async def get_cards_thumbnails(session):
    try:
        cards_list_dir = os.path.join(os.path.dirname(__file__), '../metas/cards_list.json')
        with open(cards_list_dir, 'r') as f:
            data = json.load(f)
        for item in data:
            asset_name = item['assetbundleName']
            asset_exist = check_local_card_asset(asset_name)
            if asset_exist:
                pass
            else:
                get_card_thb(asset_name)
        await session.send('所有卡牌头图更新完成。')
    except Exception as identifier:
        print(identifier)


@on_command('show_gacha_list',
            aliases='查看卡池',
            only_to_me=False)
async def show_gacha_list(session):
    try:
        if session.event['sender']['user_id'] is not None:
            user_qq = str(session.event['sender']['user_id'])
        else:
            user_qq = str(session.event['user_id'])
        await check_cooldown(session, user_qq, limiter, time=60)
        gachas, master_data, cards = gacha_load_metas()
        event_id = master_data['event_no']
        ongoing_gacha_id = master_data['ongoing_gacha_id']
        gacha_info = ''
        for idx in range(-3, 0):
            gacha_id = gachas[idx]['id']
            gacha_name = gachas[idx]['name']
            asset_exist = check_local_gacha_banner(gacha_id)
            if asset_exist:
                pass
            else:
                get_gacha_banner(gacha_id)
            gacha_banner_dir = os.path.join(os.path.dirname(__file__),
                                            f'assets/gacha_banner/banner_gacha{gacha_id}.png')
            tmp_dir = f'/home/phynon/opt/cqhttp/data/images/banner_gacha{gacha_id}.png'
            print(gacha_banner_dir, tmp_dir)
            shutil.copy(gacha_banner_dir, tmp_dir)
            gacha_info += f'{gacha_id} {gacha_name}\n'
            gacha_info += f'[CQ:image,file=banner_gacha{gacha_id}.png]'
        gacha_info += f"现在是第 {event_id} 期活动，卡池为 {ongoing_gacha_id}\n"
        gacha_info += '可以发送 "切换活动 活动期数" 切换追踪的活动\n'
        gacha_info += '可以发送 "切换卡池 卡池编码" 切换使用的卡池'
        await session.send(gacha_info)
    except Exception as identifier:
        print(repr(identifier))

@on_command('change_ongoing_gacha', aliases='切换卡池', only_to_me=False)
async def change_ongoing_gacha(session):
    master_dir = os.path.join(os.path.dirname(__file__), '../metas/master_data.json')
    with open(master_dir, 'r') as f:
        master_data = json.load(f)
    gacha_id = session.get('gacha_id')
    master_data['ongoing_gacha_id'] = int(gacha_id)
    with open(master_dir, 'w') as f:
        json.dump(master_data, f, indent=2, ensure_ascii=False)
    await session.send(f'已切换到卡池 {gacha_id}')

@change_ongoing_gacha.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['gacha_id'] = stripped_arg
        return
    if not stripped_arg:
        session.pause('爬')
    session.state[session.current_key] = stripped_arg