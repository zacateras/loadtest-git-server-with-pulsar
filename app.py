"""Simple actor message passing"""
from pulsar import arbiter, ensure_future
from client_actor import ClientActor
import time


def start(arbiter, **kwargs):
    ensure_future(app(arbiter))


async def app(arbiter):

    actors = [ClientActor(i) for i in range(10)]

    for actor in actors:
        actor.spawn()

    time.sleep(10)

    for actor in actors:
        await actor.terminate()


if __name__ == '__main__':
    arbiter(start=start).start()
