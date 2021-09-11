import random
import os

import json
import nonebot
from nonebot import on_command, CommandSession
from miku.utils import check_favor, favor_up, favor_down

# from .luka import Music_api


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
    ]
    wife = random.sample(wife_list, 1)[0]
    await session.send(wife)


@on_command('crawl',
            aliases=('爬', 'kkp', '爬爬爬'),
            only_to_me=True)
async def crawl_react(session):
    crawl_list = [
        '不理你了 哼',
        '你才爬',
        'バ∼カ∼',
        '[CQ:image,file=miku_crawl.jpg]'
    ]
    crawl = random.sample(crawl_list, 1)[0]
    await session.send(crawl)


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

@on_command('set_member_ban_broken_love',
            aliases='失恋',
            only_to_me=True)
async def set_member_ban_broken_love(session):
    try:
        bot = session.bot
        group_id = session.event.group_id
        await session.send('？')
        await bot.set_group_ban(group_id=group_id, user_id=session.state['user_qq'],
                                duration=session.state['time']*60)
    except KeyError as identifier:
        pass
    else:
        pass

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