import os

import asyncio
import random

from pulsar import Actor
from GitConnector import GitCreator, init_repo
from git_client import *


def actor_scatter_process(actor, task):
    return ActorControl(actor).task_receive(task)


def actor_gather_process(actor):
    return ActorControl(actor).task_report()


class ActorState:
    def __init__(self):
        self.task = None
        self.results = []


class ActorControl:
    def __init__(self, actor: Actor):
        if actor is not None:
            if not hasattr(actor, 'state_ref') or actor.state_ref is None:
                actor.state_ref = ActorState()

            self._actor = actor
            self._state = actor.state_ref

    def task_receive(self, task):
        self._print('Starting work on task %s.' % str(task))
        self._actor._loop.create_task(self._task_process(task))

        return 0

    def task_report(self):
        return self._state.results

    async def _task_process(self, task):
        self._state.task = task

        repo_path = 'git/client/%s' % task['id']
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)

        os.chdir(repo_path)
        git_client_clone()

        while True:
            self._print('Committing...')

            rand_int = random.randint(0, 10)

            await asyncio.sleep(rand_int)
            self._state.results.append(rand_int)

    def periodic_task(self):
        # TODO Implement

        # change /Users/savchuk/PycharmProjects/load-test-git to your's project location
        dir_path = "/Users/savchuk/PycharmProjects/load-test-git/REPO_ROOT/git/client/{}".format(self._actor.aid)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            dir_file = "file_1.txt"
            with (open(dir_file, 'a')) as fl:
                fl.write("string " * 8)
                fl.close()

            init_repo(dir_path)
            git_conn = GitCreator(self._actor.aid, 'REPO_ROOT/git/client/{}'.format(self._actor.aid), dir_file,
                                  'Commit String 2')
            git_conn.create_new_repo_gihub()
            git_conn.repo_add()
            git_conn.repo_commit()
            git_conn.repo_push()

        # print(self.actor.cfg.timeout)
        # print(self.actor.actorparams())
        # print(self.actor.info())

        self._print('REPORTING!')
        self._print_state()

    def _print_state(self):
        print('[' + ', '.join((
            'aid: %s' % self._actor.aid,
            'name: %s' % self._actor.name,
            'address: %s' % str(self._actor.address),
            'is_process: %s' % self._actor.is_process(),
            'is_arbiter: %s' % self._actor.is_arbiter(),
            'is_monitor: %s' % self._actor.is_monitor(),
            'is_running: %s' % self._actor.is_running())) + ']')

    def _print(self, output):
        print(('[%s] ' % ', '.join((self._actor.aid, self._actor.name))) + output)
