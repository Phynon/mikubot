import json
import os
from typing import FrozenSet

import requests
from nonebot import CommandSession, on_command


@on_command('line', aliases=('sekai线'), only_to_me=False)
async def sekai_line_react(session):
    master_dir = os.path.join(os.path.dirname(__file__), 'master_data.json')
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

@on_command('pred', aliases=('sekai预测'), only_to_me=False)
async def sekai_pred_react(session):
    master_dir = os.path.join(os.path.dirname(__file__), 'master_data.json')
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