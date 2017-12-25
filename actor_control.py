from pulsar import Actor, ensure_future


class ActorState:
    pass


class ActorControl:
    def __init__(self, actor: Actor, actor_state: ActorState):
        self.actor = actor
        self.actor_state = actor_state

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
    def __init__(self):
        self.actor_state = ActorState()

    def start(self, actor, **kwargs):
        arbiter_control = ActorControl(actor, self.actor_state)
        arbiter_control.start()

    def periodic_task(self, actor):
        arbiter_control = ActorControl(actor, self.actor_state)
        arbiter_control.periodic_task()

    def stop(self):
        arbiter_control = ActorControl(None, self.actor_state)
        arbiter_control.stop()
