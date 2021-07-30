import random
import requests
import json
import os
from PIL import Image
from miku.utils import FreqLimiter
from nonebot import on_command

limiter = FreqLimiter(10)

@on_command('gacha_ten',
            aliases='十连',
            only_to_me=True)
async def gacha_ten(session):
    if session.event['sender']['user_id'] is not None:
        user_qq = str(session.event['sender']['user_id'])
    else:
        user_qq = str(session.event['user_id'])
    if not limiter.check(user_qq):
        await session.finish(f'冷却中(剩余 {int(limiter.left_time(user_qq)) + 1}秒)', at_sender=True)
    limiter.start_cd(user_qq, 5)
    gacha_list_dir = os.path.join(os.path.dirname(__file__), 'gacha_list.json')
    master_data_dir = os.path.join(os.path.dirname(__file__), '../sekaievent/master_data.json')
    cards_list_dir = os.path.join(os.path.dirname(__file__), 'cards_list.json')
    with open(gacha_list_dir, 'r') as f:
        gachas = json.load(f)
    with open(master_data_dir, 'r') as f:
        master_data = json.load(f)
    with open(cards_list_dir, 'r') as f:
        cards = json.load(f)
    on_gacha_idx = master_data['ongoing_gacha_id']
    for item in gachas:
        if item['id'] == on_gacha_idx:
            gacha = item
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
    line = ''
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
    '''
    rates: normal rates
    up_rate: total up card rates
    up_charas: up card info
    '''
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
        return
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
            target.paste(images[5*row+col], ((128+5)*col, (128+5)*row))
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
        gacha_list_dir = os.path.join(os.path.dirname(__file__), 'gacha_list.json')
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
        raw_data = requests.get(url)
        data = json.loads(raw_data.content)
        cards_list_dir = os.path.join(os.path.dirname(__file__), 'cards_list.json')
        with open(cards_list_dir, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        get_cards_info = (f"sekai中已有{len(list(data))}张卡牌。\n"
                          f"你今天想要看到谁的故事呢？")
        await session.send(get_cards_info)
        for item in data:
            asset_name = item['assetbundleName']
            chara_thumbnail_dir = os.path.join(os.path.dirname(__file__), f'thumbnail/chara/{asset_name}_normal.png')
            if not os.path.exists(os.path.join(os.path.dirname(__file__), 'thumbnail/chara')):
                os.makedirs(os.path.join(os.path.dirname(__file__), 'thumbnail/chara'))
            if os.path.exists(chara_thumbnail_dir):
                pass
            else:
                print(asset_name)
                url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/thumbnail/chara_rip/{asset_name}_normal.png'
                raw_data = requests.get(url)
                with open(chara_thumbnail_dir, 'wb') as f:
                    f.write(raw_data.content)
        get_cards_thb = ("所有卡牌头图更新完成。")
        await session.send(get_cards_thb)
    except Exception as identifier:
        print(identifier)

@on_command('get_cards_thumbnails',
            aliases='更新卡牌头图',
            only_to_me=False)
async def get_cards_thumbnails(session):
    try:
        cards_list_dir = os.path.join(os.path.dirname(__file__), 'cards_list.json')
        with open(cards_list_dir, 'r') as f:
            data = json.load(f)
        for item in data:
            asset_name = item['assetbundleName']
            chara_thumbnail_dir = os.path.join(os.path.dirname(__file__), f'thumbnail/chara/{asset_name}_normal.png')
            if not os.path.exists(os.path.join(os.path.dirname(__file__), 'thumbnail/chara')):
                os.makedirs(os.path.join(os.path.dirname(__file__), 'thumbnail/chara'))
            if os.path.exists(chara_thumbnail_dir):
                pass
            else:
                print(asset_name)
                url = f'https://sekai-res.dnaroma.eu/file/sekai-assets/thumbnail/chara_rip/{asset_name}_normal.png'
                raw_data = requests.get(url)
                with open(chara_thumbnail_dir, 'wb') as f:
                    f.write(raw_data.content)
        get_cards_thb = ("所有卡牌头图更新完成。")
        await session.send(get_cards_thb)
    except Exception as identifier:
        print(identifier)
