from pulsar import Actor, ensure_future


class ActorState:
    def __init__(self):
        self.task = None


class ActorControl:
    def __init__(self, actor: Actor):
        if actor is not None:
            if not hasattr(actor, 'state_ref') or actor.state_ref is None:
                actor.state_ref = ActorState()

            self.actor = actor
            self.state = actor.state_ref

    def start(self):
        pass

    def periodic_task(self):
        # TODO Implement

        # print(self.actor.cfg.timeout)
        # print(self.actor.actorparams())
        # print(self.actor.info())

        self.__print('REPORTING!')
        self.__print_state()

    def stop(self):
        pass

    def task_process(self, task):
        self.state.task = task
        self.__print('Starting work on task %s.' % str(task))

        return 'ok'

    def task_prepare_report(self):
        return self.state.task;

    def __print_state(self):
        print('[' + ', '.join((
              'aid: %s' % self.actor.aid,
              'name: %s' % self.actor.name,
              'address: %s' % str(self.actor.address),
              'is_process: %s' % self.actor.is_process(),
              'is_arbiter: %s' % self.actor.is_arbiter(),
              'is_monitor: %s' % self.actor.is_monitor(),
              'is_running: %s' % self.actor.is_running())) + ']')

    def __print(self, output):
        print(('[%s] ' % ', '.join((self.actor.aid, self.actor.name))) + output)


class ActorControlFacade:
    def start(self, actor, **kwargs):
        ActorControl(actor).start()

    def periodic_task(self, actor):
        ActorControl(actor).periodic_task()

    '''
    Stop method seems to not support Actor parameter.
    '''
    def stop(self):
        ActorControl(None).stop()

    def task_process(self, actor, task):
        return ActorControl(actor).task_process(task)

    def task_prepare_report(self, actor):
        return ActorControl(actor).task_prepare_report()
