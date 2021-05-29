import random

from nonebot import on_command, CommandSession
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
        song_list = Music_api().get_music_list(song_name)
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
