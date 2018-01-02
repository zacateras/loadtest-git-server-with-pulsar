from pulsar.api import send
from actor_control import *
from git_server import *
from app_log_dumper import dump_log
import optimization
import random
import asyncio


class CycleConfig:
    def __init__(self, no, timeout, git_server_cpus, actor_count):
        self.no = no
        self.timeout = timeout
        self.git_server_cpus = git_server_cpus
        self.actor_count = actor_count


class CycleResult:
    def __init__(self):
        pass


class ArbiterControl:
    def __init__(self):
        self._git_server = None
        self._actors = []

        self._log = []
        self._optimization_algorithm = optimization.Annealing(self._log, ["actor_count"], [1], [1], [(1, None)])

    def __call__(self, arb, **kwargs):
        self._print('START')

        self._arb = arb
        self._arb_task = arb._loop.create_task(self._work())

    async def _work(self):
        cycle_i = 0

        while True:
            # CYCLE - START
            cycle_config = self._next_cycle_config(cycle_i)
            self._print('Starting cycle %s...' % cycle_i)

            if os.path.exists(git_rel_path):
                shutil.rmtree(git_rel_path)

            self._print('Starting git server...')
            self._git_server = git_server_build(cycle_config.git_server_cpus)

            await self._scatter(cycle_config)

            # CYCLE - WAIT FOR TIMEOUT
            for i in range(cycle_config.timeout):
                self._print('%s...' % i)
                await asyncio.sleep(1)

            # CYCLE - END
            cycle_result = await self._gather()

            self._print('Stopping git server...')
            self._git_server.dispose()

            # CYCLE - LOG RESULT
            self._log.append({'cycle_config': cycle_config, 'cycle_result': cycle_result})

            dump_log(self._log)

            cycle_i += 1

    def _next_cycle_config(self, cycle_no):
        # optimization algorithm based on self._log (especially last entry - last cycle)D
        values = self._optimization_algorithm.get_optimal_parameters()
        return CycleConfig(cycle_no, 5, 0.05, values["actor_count"])

    async def _scatter(self, cycle_config: CycleConfig):
        self._print('Spawning actors...')
        self._actors = []
        for ai in range(cycle_config.actor_count):
            act = await self._arb.spawn()
            self._actors.append(act)

        self._print('Scattering tasks...')
        for i in range(cycle_config.actor_count):
            request = {
                'actor_id': i,
                'actor_count': cycle_config.actor_count,
                'actor_type': 'ONE_FILE',
                'actor_interval': random.randint(1, 10)
            }

            await send(self._actors[i], 'run', actor_scatter_process, request)

    async def _gather(self):
        self._print('Gathering results...')
        cycle_result = []
        for act in self._actors:
            # DO NOT AWAIT
            # run all cancel commands async
            send(act.aid, 'run', actor_cancel_process)

        for act in self._actors:
            while True:
                report_events = await send(act, 'run', actor_gather_process)
                if report_events is not None:
                    break

                await asyncio.sleep(0.5)

            cycle_result.extend(report_events)

        self._print('Stopping actors...')
        for act in self._actors:
            await send(act, 'stop')

        return cycle_result

    @staticmethod
    def _print(output):
        print('[ARBITER] ' + output)
