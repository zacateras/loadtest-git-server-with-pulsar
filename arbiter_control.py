from pulsar import arbiter, ensure_future, spawn
from actor_control import *


class ArbiterState:
    def __init__(self):
        self.actor_control_facades = []
        self.actors = []

        self.actorCount = -1
        self.tickLimit = -1


class ArbiterControl:
    def __init__(self, arbiter, state: ArbiterState):
        self.arbiter = arbiter
        self.state = state

    def start(self):
        self.__print('START.')

    async def periodic_task(self):
        if self.state.tickLimit <= 0:
            await self.__reset_cycle()

        self.__print('PERIODIC_TASK.')

        # decrease tick limit
        self.state.tickLimit -= 1
        self.__print('Remained tick limit: %s.' % self.state.tickLimit)

        # stop actors
        if self.state.tickLimit <= 0:
            self.__stop_actors()

    def stop(self):
        self.__print('STOP.')
        self.__stop_actors()

    async def __reset_cycle(self):
        self.state.actor_control_facades = []
        self.state.actors = []
        self.state.actorCount = 5
        self.state.tickLimit = 15

        await self.__spawn_actors()

    async def __spawn_actors(self):
        for ai in range(self.state.actorCount):
            acf = ActorControlFacade()
            actor = await spawn(
                start=acf.start,
                periodic_task=acf.periodic_task,
                stop=acf.stop)

            self.state.actor_control_facades.append(acf)
            self.state.actors.append(actor)

    def __stop_actors(self):
        for actor in self.state.actors:
            actor.stop()

    @staticmethod
    def __print(output):
        print('[ARBITER] ' + output)


class ArbiterControlFacade:
    def __init__(self):
        self.arbiter_state = ArbiterState()

    def start(self, arbiter, **kwargs):
        arbiter_control = ArbiterControl(arbiter, self.arbiter_state)
        arbiter_control.start()

    def periodic_task(self, arbiter):
        arbiter_control = ArbiterControl(arbiter, self.arbiter_state)
        ensure_future(arbiter_control.periodic_task())

    def stop(self):
        arbiter_control = ArbiterControl(None, self.arbiter_state)
        arbiter_control.stop()
