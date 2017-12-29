import os

import asyncio
import random
import time

from pulsar import Actor
from git_client import *


def actor_scatter_process(actor, task):
    return ActorControl(actor).task_receive(task)


def actor_gather_process(actor):
    return ActorControl(actor).task_report()


class Event:
    def __init__(self, event_time, actor_id, actor_type, actor_interval, command_type, command_exit_code, command_result, command_duration):
        """

        :param event_time: event timestamp
        :param actor_id: [0 - actor_count]
        :param actor_type: ONE_FILE, MULTI_FILE, MULTI_BRANCH
        :param actor_interval: interval of commands executed by an actor
        :param command_type: CLONE / FETCH / PULL / PUSH
        :param command_exit_code: exit code of a command
        :param command_result: SUCCESS / FAILURE
        :param command_duration: duration of an event (command)
        """

        self.event_time = event_time
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.actor_interval = actor_interval
        self.command_type = command_type
        self.command_exit_code = command_exit_code
        self.command_result = command_result
        self.command_duration = command_duration


class ActorState:
    def __init__(self):
        self.task = None
        self.events = []


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
        return self._state.events

    async def _task_process(self, task):
        self._state.task = task

        exit_code = -1

        # Prepare client repository
        repo_path = '%s/%s' % (git_client_rel_path, task['actor_id'])
        if not os.path.exists(repo_path):
            os.makedirs(repo_path)

        os.chdir(repo_path)

        self._print('Cloning...')
        while self._git_clone() != 0:
            self._print('Retrying...')
            await asyncio.sleep(0.1)
            if not self._actor.is_running():
                return

        while True:
            self._print('Committing...')

            rand_int = random.randint(0, 10)

            # Edit file and update repo
            dir_file = "file_%s.txt" % task['actor_id']
            with (open(dir_file, 'a')) as fl:
                fl.writelines('%s, %s\n' % (time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime()), self._actor.aid))
                fl.close()
            git_client_exec('git add .')
            git_client_exec('git commit -m "Some commit %s" -q' % rand_int)

            cmd_result = self._git_push()
            while cmd_result != 0:
                if not self._actor.is_running():
                    return

                await asyncio.sleep(0.1)

                if self._git_fetch() != 0:
                    continue

                cmd_result = self._git_merge()
                cmd_result = self._git_pull()

            await asyncio.sleep(rand_int)

    def _print_state(self):
        print('[' + ', '.join((
            'aid: %s' % self._actor.aid,
            'name: %s' % self._actor.name,
            'address: %s' % str(self._actor.address),
            'is_process: %s' % self._actor.is_process(),
            'is_arbiter: %s' % self._actor.is_arbiter(),
            'is_monitor: %s' % self._actor.is_monitor(),
            'is_running: %s' % self._actor.is_running())) + ']')

    def _git_clone(self):
        start = time.time()
        exit_code = git_client_clone()
        end = time.time()

        self._log_event('clone', exit_code, end - start)

        return exit_code

    def _git_fetch(self):
        start = time.time()
        exit_code = git_client_exec('git fetch -q')
        end = time.time()

        self._log_event('fetch', exit_code, end - start)

        return exit_code

    def _git_pull(self):
        start = time.time()
        exit_code = git_client_exec('git pull -q')
        end = time.time()

        self._log_event('pull', exit_code, end - start)

        return exit_code

    def _git_push(self):
        start = time.time()
        exit_code = git_client_exec('git push -q')
        end = time.time()

        self._log_event('push', exit_code, end - start)

        return exit_code

    def _git_merge(self):
        start = time.time()
        exit_code = git_client_exec('git merge -s recursive -Xtheirs -q')
        end = time.time()

        self._log_event('merge', exit_code, end - start)

        return exit_code

    def _log_event(self, command_type, command_exit_code, command_duration):
        self._state.events.append(
            Event(event_time=time.gmtime(),
                  actor_id=self._state.task['actor_id'],
                  actor_type=self._state.task['actor_type'],
                  actor_interval=self._state.task['actor_interval'],
                  command_type=command_type,
                  command_exit_code=command_exit_code,
                  command_result=True if command_exit_code == 0 else False,
                  command_duration=command_duration))

    def _print(self, output):
        print(('[%s] ' % ', '.join((self._actor.aid, self._actor.name))) + output)
