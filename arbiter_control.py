from pulsar import arbiter, ensure_future, spawn, send
from actor_control import *
import random


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
            await self.__gather()
            self.__stop_actors()

    def stop(self):
        self.__print('STOP.')
        self.__stop_actors()

    async def __reset_cycle(self):
        self.state.actor_control_facades = []
        self.state.actors = []
        self.state.actorCount = 1
        self.state.tickLimit = 15

        await self.__spawn_actors()
        await self.__scatter()

    async def __spawn_actors(self):
        for ai in range(self.state.actorCount):
            acf = ActorControlFacade()
            actor = await spawn(
                start=acf.start,
                periodic_task=acf.periodic_task,
                stop=acf.stop)

            self.state.actor_control_facades.append(acf)
            self.state.actors.append(actor)

    async def __scatter(self):
        for i in range(self.state.actorCount):
            request = (random.randint(0, 10), random.randint(0, 10))
            response = await send(
                self.state.actors[i],
                'run',
                self.state.actor_control_facades[i].task_process,
                request)

            self.__print(str(response))

    async def __gather(self):
        for i in range(self.state.actorCount):
            response = await send(
                self.state.actors[i],
                'run',
                self.state.actor_control_facades[i].task_prepare_report)

            self.__print(str(response))

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
        ArbiterControl(arbiter, self.arbiter_state).start()

    def periodic_task(self, arbiter):
        ensure_future(ArbiterControl(arbiter, self.arbiter_state).periodic_task())

    def stop(self):
        ArbiterControl(None, self.arbiter_state).stop()
