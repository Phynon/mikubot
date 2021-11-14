import random
import json
import os
import threading
import shutil
from PIL import Image, ImageFilter, ImageDraw
from miku.utils import FreqLimiter, favor_up
import nonebot
from fuzzywuzzy import process
from miku.modules.sekaiutils import check_cooldown
from miku.modules.sekaiutils import check_local_card_asset
from miku.modules.sekaiutils import get_card_thb
from miku.modules.sekaiutils import check_local_gacha_banner
from miku.modules.sekaiutils import get_card_asset
from miku.modules.sekaiutils import game_load_cards
import asyncio


class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        self._task.cancel()


class GameMaster:
    def __init__(self):
        self.gaming = False
        self.chara = 0
        self.card = {}
        self.win = threading.Event()
        self.timer = None

    async def refresh(self):
        self.gaming = False
        self.chara = 0
        self.card = {}
        self.win.clear()

    def start(self):
        self.gaming = True
        return self

    def set_winner(self):
        self.win.set()

    def set_timer(self, timeout, task):
        self.timer = Timer(timeout, task)

game_master = GameMaster()
limiter = FreqLimiter(10)
bot = nonebot.get_bot()


def game_crop(img):
    pos = [random.randint(0, 839), random.randint(0, 429)]
    pos = (pos[0], pos[1], pos[0] + 100, pos[1] + 100)
    img = img.crop(pos)
    return img


def game_blur(img):
    img = img.filter(ImageFilter.GaussianBlur(radius=70))
    img = img.resize((500, 282), Image.ANTIALIAS)
    img.save(os.path.join(os.path.dirname(__file__), f'blur.png'))
    return img


def game_chessboard(img):
    img = img.crop((20, 15, 920, 515))
    l_block = 50
    n_rows = int(img.size[0] / l_block)
    n_cols = int(img.size[1] / l_block)
    blocks = [[0 for col in range(n_cols)] for row in range(n_rows)]
    chessboard = Image.new('RGB', (img.size[0], img.size[1]), '#ffffff')
    for row in range(0, n_rows):
        for col in range(0, n_cols):
            pos = (row * l_block, col * l_block, (row + 1) * l_block, (col + 1) * l_block)
            blocks[row][col] = img.crop(pos).rotate(random.randrange(0, 360, 90))
            chessboard.paste(blocks[row][col], (pos[0], pos[1]))
    chessboard.save(os.path.join(os.path.dirname(__file__), f'card.png'))
    return chessboard

def game_thumbnail_pixelate(img):
    size_original = img.size
    img = img.resize((4, 4))
    img = img.resize(size_original, Image.NEAREST)
    img.save(os.path.join(os.path.dirname(__file__), f'pixelate.png'))
    return img

@bot.on_message('group')
async def guess_whois(ctx):
    trigger_strs = ['角色猜猜看', '猜局部', '猜模糊', '猜头像']
    message_text = ctx.message.extract_plain_text()
    flag = -1
    for idx, trigger_str in enumerate(trigger_strs):
        if message_text == trigger_str:
            flag = idx
    if flag == -1:
        return
    if game_master.gaming:
        return
    await bot.send_group_msg(group_id=ctx['group_id'],
                             message='游戏正在准备中')
    game_master.start()
    cards = game_load_cards()
    if flag == 0:
        answer = random.sample(cards, 1)[0]
        # print(answer)
        if answer['cardRarityType'] in ('rarity_1', 'rarity_2', 'rarity_birthday'):
            status = 'normal'
            game_method = game_blur
        else:
            status = random.sample(['normal', 'after_training'], 1)[0]
            if random.randint(0, 1) == 0:
                game_method = game_blur
            else:
                game_method = game_crop
    elif flag == 1:
        while True:
            answer = random.sample(cards, 1)[0]
            if answer['cardRarityType'] not in ('rarity_1', 'rarity_2', 'rarity_birthday'):
                break
        status = random.sample(['normal', 'after_training'], 1)[0]
        game_method = game_crop
    elif flag == 2:
        answer = random.sample(cards, 1)[0]
        # print(answer)
        if answer['cardRarityType'] in ('rarity_1', 'rarity_2', 'rarity_birthday'):
            status = 'normal'
        else:
            status = random.sample(['normal', 'after_training'], 1)[0]
        game_method = game_blur
    elif flag == 3:
        answer = random.sample(cards, 1)[0]
        # print(answer)
        if answer['cardRarityType'] in ('rarity_1', 'rarity_2', 'rarity_birthday'):
            status = 'normal'
        else:
            status = random.sample(['normal', 'after_training'], 1)[0]
        game_method = game_thumbnail_pixelate
    asset_name = answer['assetbundleName']
    ans_title = answer['prefix']
    game_master.chara = answer['characterId'] - 1
    game_master.card = answer
    chara_list_dir = os.path.join(os.path.dirname(__file__), f'../metas/chara_list.json')
    with open(chara_list_dir, 'r') as f:
        charas = json.load(f)
    ans_name = charas[game_master.chara]['firstName'] + charas[game_master.chara]['givenName']
    all_aliases = charas[game_master.chara]['aliases']
    all_aliases.append(ans_name)
    all_aliases.append(charas[game_master.chara]['givenName'])
    print(all_aliases)
    asset_exist = check_local_card_asset(asset_name, status)
    if asset_exist:
        pass
    else:
        get_card_asset(asset_name, status)
    card_asset_dir = os.path.join(os.path.dirname(__file__),
                                  f'assets/character/member_small/{asset_name}/card_{status}.png')
    img = Image.open(card_asset_dir)
    if flag == 3:
        thumbnail_dir = os.path.join(os.path.dirname(__file__),
                                    f'thumbnail/chara/{asset_name}_{status}.png')
        img = Image.open(thumbnail_dir)
    img = game_method(img)
    ques_dir = '/home/phynon/opt/cqhttp/data/images/ques.png'
    ans_dir = '/home/phynon/opt/cqhttp/data/images/ans.png'
    img.save(ques_dir)
    shutil.copy(card_asset_dir, ans_dir)
    initiator_qq = ctx.sender['user_id']
    print(initiator_qq)
    favor_up(initiator_qq, 1)
    await bot.send_group_msg(group_id=ctx['group_id'],
                             message='请在30秒之内发送图示角色的名字[CQ:image,file=ques.png]')

    async def send_answer():
        await game_master.refresh()
        await bot.send_group_msg(group_id=ctx['group_id'],
                                 message=f'正确答案是 {ans_title} {ans_name}[CQ:image,file=ans.png]')

    game_master.set_timer(30, send_answer)

@bot.on_message('group')
async def input_guess(ctx):
    print(game_master.gaming, game_master.win.isSet())
    if not game_master.gaming or game_master.win.isSet():
        return
    input_answer = ctx.message.extract_plain_text()
    answer = game_master.card
    ans_title = answer['prefix']
    chara_list_dir = os.path.join(os.path.dirname(__file__), f'../metas/chara_list.json')
    with open(chara_list_dir, 'r') as f:
        charas = json.load(f)
    ans_name = charas[game_master.chara]['firstName'] + charas[game_master.chara]['givenName']
    all_aliases = charas[game_master.chara]['aliases']
    all_aliases.append(ans_name)
    all_aliases.append(charas[game_master.chara]['givenName'])
    _, confidence = process.extractOne(input_answer, all_aliases)
    print(confidence)
    if confidence > 98:
        game_master.set_winner()
        winner_qq = ctx.sender['user_id']
        # print(winner_qq)
        favor_up(winner_qq, 1)
        await bot.send_group_msg(group_id=ctx['group_id'],
                                 message=f'回答正确\n正确答案是 {ans_title} {ans_name}\n[CQ:image,file=ans.png]')
        await game_master.refresh()
        game_master.timer.cancel()
