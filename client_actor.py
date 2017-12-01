import random
import time

from pulsar import spawn, Actor


class ClientActor:

    def __init__(self):
        self.actor = None

    async def spawn(self):
        self.actor = await spawn(start=self.__do_work)

    async def terminate(self):
        await self.actor.stop()

    def __do_work(self, actor: Actor, **kwargs):
        while True:
            print('abc')

            time.sleep(random.randint(1, 5))
