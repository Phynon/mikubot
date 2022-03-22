from nonebot import on_notice, NoticeSession


@on_notice('group_decrease.leave')
async def person_leave(session: NoticeSession):
    msg = f'{session.event.user_id} 离开了'
    await session.send(msg)

@on_notice('group_increase')
async def person_join(session: NoticeSession):
    print(session.event.group_id)
    if session.event.group_id == 707321525:
        msg = '新しい初音ミク、ようこそ'
    elif session.event.group_id == 773737472:
        msg = '新しいテスター、ようこそ'
    elif session.event.group_id == 775960101:
        msg = '新しい住人、ようこそ'
    else:
        msg = '新しい初音ミク、ようこそ'
    await session.send(msg)
