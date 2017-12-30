import csv
from datetime import datetime
from collections import namedtuple

_log_class_fields = namedtuple('log_class_fields', ['time', 'score', 'title', 'text', 'ofReddit', 'serious'])


# TODO hmm maybe this can be generated automatically ?
class LogEntry:
    def __init__(self,
                 cycle_no,
                 cycle_actor_count,
                 cycle_git_server_cpus,
                 cycle_timeout,
                 event_time,
                 actor_id,
                 actor_type,
                 actor_interval,
                 command_type,
                 command_exit_code,
                 command_result,
                 command_duration):

        self.cycle_no = cycle_no
        self.cycle_actor_count = cycle_actor_count
        self.cycle_git_server_cpus = cycle_git_server_cpus
        self.cycle_timeout = cycle_timeout
        self.event_time = event_time
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.actor_interval = actor_interval
        self.command_type = command_type
        self.command_exit_code = command_exit_code
        self.command_result = command_result
        self.command_duration = command_duration

    @staticmethod
    def header():
        yield 'cycle_no'
        yield 'cycle_actor_count'
        yield 'cycle_git_server_cpus'
        yield 'cycle_timeout'
        yield 'event_time'
        yield 'actor_id'
        yield 'actor_type'
        yield 'actor_interval'
        yield 'command_type'
        yield 'command_exit_code'
        yield 'command_result'
        yield 'command_duration'

    def __iter__(self):
        yield self.cycle_no
        yield self.cycle_actor_count
        yield self.cycle_git_server_cpus
        yield self.cycle_timeout
        yield datetime(*self.event_time[:6]).isoformat()
        yield self.actor_id
        yield self.actor_type
        yield self.actor_interval
        yield self.command_type
        yield self.command_exit_code
        yield self.command_result
        yield self.command_duration
        

def dump_log(log):
    rows = []

    for cycle_log in log:
        cycle_config = cycle_log['cycle_config']
        cycle_result = cycle_log['cycle_result']

        for log_entry in _create_log_entries(cycle_config, cycle_result):
            rows.append(log_entry)

    with open('app.log', 'w', newline='', encoding='utf8') as f:
        writer = csv.writer(f)
        writer.writerow(LogEntry.header())
        writer.writerows(rows)


def _create_log_entries(cycle_config, cycle_result):
    for event in cycle_result:
        yield _create_log_entry(cycle_config, event)


def _create_log_entry(cycle_config, event):
    return LogEntry(
        cycle_config.no,
        cycle_config.actor_count,
        cycle_config.git_server_cpus,
        cycle_config.timeout,
        event.event_time,
        event.actor_id,
        event.actor_type,
        event.actor_interval,
        event.command_type,
        event.command_exit_code,
        event.command_result,
        event.command_duration)
