import random
import os

import json
import nonebot
import asyncio
from nonebot import on_command, CommandSession
from nonebot.message import CanceledException, message_preprocessor
from miku.utils import check_favor, favor_up, favor_down


# from .luka import Music_api

blacklist = []

async def remove_from_blacklist_active(user_id):
    blacklist.remove(user_id)
    print(f'{user_id} removed from blacklist')

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

class BlackListMaster:
            def __init__(self):
                self.timer = None

            def set_timer(self, timeout, task):
                self.timer = Timer(timeout, task)

blacklist_master = BlackListMaster()

def is_to_me(raw_message):
    if '[CQ:at,qq=1297374188]' in raw_message:
        return True
    elif raw_message.startswith('miku'):
        return True
    elif raw_message.endswith('miku'):
        return True
    else:
        return False


@message_preprocessor
async def black(bot, event, _):
    print(blacklist)
    if event['message'][0]['type'] == 'text':
        message = event['raw_message']
    if event.user_id in blacklist:
        if is_to_me(message):
            if '对不起' in message or 'orry' in message or 'ごめん' in message:
                groups_meta_dir = os.path.join(os.path.dirname(__file__), '../metas/groups_meta.json')
                with open(groups_meta_dir, 'r') as f:
                    groups_meta = json.load(f)
                await bot.send_group_msg(group_id=groups_meta['sekai'],
                                         message='下次不要这样啦')
                blacklist.remove(event.user_id)
            else:
                raise CanceledException(f'{event.user_id} in blacklist')
        else:
            raise CanceledException(f'{event.user_id} in blacklist')


@on_command('zai?',
            aliases=('在?', '在？', '在吗', '在么？', '在嘛', '在嘛？'),
            only_to_me=True)
async def say_hi(session):
    hi_list = [
        '変わらむまま　ここで待ってるから',
        '手を繋ごうか　今だけでも',
        'あの一等星のさんざめく光で　あなたとダンスを踊ろうか',
        'そらを越えて　星を越えて　君に届け　このメッセージ',
    ]
    hi = random.sample(hi_list, 1)[0]
    await session.send(hi)


@on_command('wife',
            aliases=('老婆', '老婆！', '么么'),
            only_to_me=True)
async def wife_react(session):
    wife_list = [
        '么么',
        '抱抱你',
        '想听我唱歌了？',
        '[CQ:image,file=miku_mmj_kawaii.png]',
    ]
    msg = random.sample(wife_list, 1)[0]
    await session.send(msg)


@on_command('marriage',
            aliases=('娶我', '嫁我', '嫁给我'),
            only_to_me=True)
async def marriage_react(session):
    marriage_list = [
        '不行的',
        '但是这里没有你',
        '[CQ:image,file=miku_wa.png]',
    ]
    msg = random.sample(marriage_list, 1)[0]
    await session.send(msg)


@on_command('lovely',
            aliases=('可爱', '你真棒', '真棒'),
            only_to_me=True)
async def lovely_react(session):
    lovely_list = [
        'わんだほーい',
        '[CQ:image,file=miku_ehehe.png]',
    ]
    msg = random.sample(lovely_list, 1)[0]
    await session.send(msg)


@on_command('like',
            aliases=('喜欢你', '我喜欢你', '好喜欢你', '我好喜欢你', '好喜欢', '爱你', '我爱你'),
            only_to_me=True)
async def lovely_react(session):
    like_list = [
        '太好了~'
        '要我给你唱首歌吗',
        '[CQ:image,file=miku_ehehe.png]',
        '[CQ:image,file=miku_mmj_kawaii.png]',
    ]
    msg = random.sample(like_list, 1)[0]
    await session.send(msg)


@on_command('crawl',
            aliases=('爬', '爬爬爬'),
            only_to_me=True)
async def crawl_react(session):
    crawl_list = [
        '你才爬',
        'バ∼カ∼',
        '不会 你教我',
        '[CQ:image,file=miku_crawl.jpg]',
    ]
    msg = random.sample(crawl_list, 1)[0]
    await session.send(msg)


@on_command('evil',
            aliases=('大坏蛋', '坏蛋'),
            only_to_me=True)
async def evil_react(session):
    bot = session.bot
    group_id = session.event.group_id
    user_qq = session.event.user_id
    # user_qq = session.event['sender']['user_id']
    evil_list = [
        '我就坏！要你管！',
        '？',
        '[CQ:image,file=minori_sorry.jpg]',
        '[CQ:image,file=miku_wu.png]',
    ]
    msg = random.sample(evil_list, 1)[0]
    await session.send(msg)
    await bot.set_group_ban(group_id=group_id, user_id=user_qq,
                            duration=random.randint(1, 2) * 60)


@on_command('fail_school',
            aliases=('退学', '挂科'),
            only_to_me=True)
async def fail_school_react(session):
    fail_school_list = [
        '要上学的是你哦',
        '反弹',
    ]
    msg = random.sample(fail_school_list, 1)[0]
    await session.send(msg)


@on_command('sing',
            aliases=('唱歌', '来一首', '唱一首歌', '点歌'),
            only_to_me=True)
async def sing_react(session):
    try:
        song_name = session.get('song')
        print(song_name)
        # song_list = Music_api().get_music_list(song_name)
        song_list = []
        print(song_list)
        song_id = song_list[0]['id']
        await session.send('[CQ:music,type=163,id=%s]' % song_id)
    except KeyError as identifier:
        await session.send('不会唱')
    else:
        pass


@sing_react.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['song'] = stripped_arg
        return
    if not stripped_arg:
        session.pause('爬')
    session.state[session.current_key] = stripped_arg


@on_command('usage',
            aliases=('指南', '33'),
            only_to_me=True)
async def usage(session):
    try:
        await session.send('[CQ:image,file=usage_1.png]')
        await session.send('[CQ:image,file=usage_2.png]')
    except KeyError as identifier:
        pass
    else:
        pass


# dirty
@on_command('set_member_ban',
            aliases=('和我一起喝茶', '精致睡眠'),
            only_to_me=True)
async def set_member_ban(session):
    try:
        bot = session.bot
        group_id = session.event.group_id
        await bot.set_group_ban(group_id=group_id, user_id=session.state['user_qq'],
                                duration=session.state['time'] * 60)
    except KeyError as identifier:
        pass
    else:
        pass


# dirty
@set_member_ban.args_parser
async def _(session: CommandSession):
    if session.event['sender']['user_id'] is not None:
        user_qq = str(session.event['sender']['user_id'])
    else:
        user_qq = str(session.event['user_id'])
    session.state['user_qq'] = user_qq
    stripped_arg = random.randint(1, 60)
    session.state['time'] = stripped_arg
    session.state[session.current_key] = stripped_arg


# dirty
@on_command('set_member_ban_broken_love',
            aliases='失恋',
            only_to_me=True)
async def set_member_ban_broken_love(session):
    try:
        bot = session.bot
        group_id = session.event.group_id
        user_id = session.state['user_qq']
        # user_id = session.event.user_id
        await session.send('？不理你了')
        # await bot.set_group_ban(group_id=group_id, user_id=session.state['user_qq'],
        #                         duration=session.state['time'] * 60)
        blacklist.append(int(user_id))

        async def remove_from_blacklist_wait():
            blacklist.remove(int(user_id))
            print(f'{user_id} removed from blacklist')
        blacklist_master.set_timer(600, remove_from_blacklist_wait)
    except KeyError as identifier:
        pass
    else:
        pass


# dirty
@set_member_ban_broken_love.args_parser
async def _(session: CommandSession):
    if session.event['sender']['user_id'] is not None:
        user_qq = str(session.event['sender']['user_id'])
    else:
        user_qq = str(session.event['user_id'])
    session.state['user_qq'] = user_qq
    stripped_arg = random.randint(1, 2)
    session.state['time'] = stripped_arg
    session.state[session.current_key] = stripped_arg


@nonebot.scheduler.scheduled_job(
    'cron',
    # year=None,
    # month=None,
    # day=None,
    # week=None,
    day_of_week="mon,tue,wed,thu,fri",
    hour=7,
    # minute=None,
    # second=None,
    # start_date=None,
    # end_date=None,
    # timezone=None,
)
async def _():
    groups_meta_dir = os.path.join(os.path.dirname(__file__), '../metas/groups_meta.json')
    with open(groups_meta_dir, 'r') as f:
        groups_meta = json.load(f)
    bot = nonebot.get_bot()
    await bot.send_group_msg(group_id=groups_meta['sekai'],
                             message='起床啦！')


@on_command('test',
            only_to_me=True)
async def _(session):
    print('logged')
    if session.event['sender']['user_id'] is not None:
        user_qq = str(session.event['sender']['user_id'])
    else:
        user_qq = str(session.event['user_id'])
    favor_up(user_qq, 20)
    return
