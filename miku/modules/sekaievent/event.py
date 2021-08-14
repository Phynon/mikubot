import json
import os
from typing import FrozenSet

import requests
from nonebot import on_command, CommandSession


@on_command('line', aliases='sekai线', only_to_me=False)
async def sekai_line_react(session):
    master_dir = os.path.join(os.path.dirname(__file__), '../metas/master_data.json')
    with open(master_dir, 'r') as f:
        master_data = json.load(f)
    url = (
        'https://bitbucket.org/sekai-world/sekai-event-track/raw/main/event%s.json'
        % (str(master_data['event_no'])))
    raw_data = requests.get(url)
    data = json.loads(raw_data.content)
    scores = '当前分数线\n'
    for i in [100, 500, 1000, 2000, 5000, 10000, 50000]:
        score_line = data[f'rank{i}'][0]['score']
        scores += f'rank{i}: {score_line}pt\n'
    await session.send(scores)

@on_command('pred', aliases='sekai预测', only_to_me=False)
async def sekai_pred_react(session):
    master_dir = os.path.join(os.path.dirname(__file__), '../metas/master_data.json')
    with open(master_dir, 'r') as f:
        master_data = json.load(f)
    url = "https://api.sekai.best/event/pred"
    raw_data = requests.get(url)
    data = json.loads(raw_data.content)
    data = data['data']
    print(data)
    preds = '预测分数线\n'
    for i in [100, 500, 1000, 2000, 5000, 10000, 50000]:
        pred_line = data[str(i)]
        preds += f'rank{i}: {pred_line}pt\n'
    await session.send(preds)

@on_command('change_ongoing_event', aliases='切换活动', only_to_me=False)
async def change_ongoing_event(session):
    master_dir = os.path.join(os.path.dirname(__file__), '../metas/master_data.json')
    with open(master_dir, 'r') as f:
        master_data = json.load(f)
    event_id = session.get('event_id')
    master_data['event_no'] = int(event_id)
    with open(master_dir, 'w') as f:
        json.dump(master_data, f, indent=2, ensure_ascii=False)
    await session.send(f'已切换到第 {event_id} 期活动')

@change_ongoing_event.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['event_id'] = stripped_arg
        return
    if not stripped_arg:
        session.pause('爬')
    session.state[session.current_key] = stripped_arg