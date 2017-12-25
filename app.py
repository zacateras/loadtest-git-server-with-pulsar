from pulsar import arbiter
from arbiter_control import *

if __name__ == '__main__':
    amf = ArbiterControlFacade()
    arbiter(start=amf.start, periodic_task=amf.periodic_task, stop=amf.stop).start()
