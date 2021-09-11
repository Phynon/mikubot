import time
import sqlite3
from collections import defaultdict

class FreqLimiter:
    def __init__(self, default_cd_seconds):
        self.next_time = defaultdict(float)
        self.default_cd = default_cd_seconds

    def check(self, key) -> bool:
        return bool(time.time() >= self.next_time[key])

    def start_cd(self, key, cd_time=0):
        self.next_time[key] = time.time() + (cd_time if cd_time > 0 else self.default_cd)

    def left_time(self, key) -> float:
        return self.next_time[key] - time.time()


def check_favor(user_qq):
    favor = 0
    with sqlite3.connect('/home/phynon/opt/test.db') as conn:
        curs = conn.cursor()
        result = curs.execute(f'select user_qq, favor from user_favor where user_qq=?', (user_qq, ))
        if len(list(result)) == 0:
            curs.execute('insert into user_favor (user_qq, favor) values (?, ?)', (user_qq, 0))
        else:
            # assert 1 row in result
            result = curs.execute(f'select user_qq, favor from user_favor where user_qq=?', (user_qq,))
            for row in result:
                favor = row[1]
    return favor


def favor_up(user_qq, up_amount=1):
    new_favor = check_favor(user_qq) + up_amount
    with sqlite3.connect('/home/phynon/opt/test.db') as conn:
        curs = conn.cursor()
        curs.execute('update user_favor set favor=? where user_qq=?', (new_favor, user_qq))
    pass


def favor_down(user_qq, degrade_amount=1):
    new_favor = check_favor(user_qq) - degrade_amount
    with sqlite3.connect('/home/phynon/opt/test.db') as conn:
        curs = conn.cursor()
        curs.execute('update user_favor set favor=? where user_qq=?', (new_favor, user_qq))
    pass
