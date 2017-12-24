import random
import time

from pulsar import spawn, Actor


class ClientActor:

    def __init__(self, name):
        self.actor = None
        self.name = name

    def spawn(self):
        self.actor = spawn(start=self.__do_work)

    async def terminate(self):
        await self.actor.stop()

    def __do_work(self, actor: Actor, **kwargs):
        while True:
            print(self.name, 'abc')

            time.sleep(random.randint(1, 5))
