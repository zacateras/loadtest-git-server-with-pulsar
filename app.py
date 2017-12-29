from pulsar import arbiter
from arbiter_control import *

if __name__ == '__main__':
    arbiter(start=ArbiterControl()).start()
