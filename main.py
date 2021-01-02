import asyncio
import miku

mikubot = miku.init()

if __name__ == '__main__':
    mikubot.run(use_reloader=False, loop=asyncio.get_event_loop())
