import random

from nonebot import on_command


@on_command('zai?',
            aliases=('在?', '在？', '在吗', '在么？', '在嘛', '在嘛？'),
            only_to_me=True)
async def say_hi(session):
    hi_list = [
        '変わらむまま　ここで待ってるから',
        '手を繋ごうか　今だけでも',
        'あの一等星のさんざめく光で　あなたとダンスを踊ろうか',
        'そらを越えて　星を越えて　君に届け　このメッサージ',
    ]
    hi = random.sample(hi_list, 1)
    await session.send(hi[0])

@on_command('wife',
            aliases=('老婆', '老婆！', '么么'),
            only_to_me=True)
async def wife_react(session):
    wife_list = [
        '么么',
        '抱抱你',
        '想听我唱歌了？',
    ]
    wife = random.sample(wife_list, 1)
    await session.send(wife[0])

@on_command('crawl',
            aliases=('爬', 'kkp', '爬爬爬'),
            only_to_me=True)
async def crawl_react(session):
    crawl_list = [
        '不理你了 哼',
        '你才爬',
        'バ∼カ∼',
    ]
    crawl = random.sample(crawl_list, 1)
    await session.send(crawl[0])

@on_command('sing',
            aliases=('唱歌', '来一首', '唱一首歌'),
            only_to_me=True)
async def sing_react(session):
    song_list = [
        '不理你了 哼',
        '你才爬',
        'バ∼カ∼',
    ]
    song = random.sample(song_list, 1)
    await session.send('[CQ:music,type=163,id=1335794789]')