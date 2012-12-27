import logging
import contextlib

import gevent
import gevent.queue
import requests.exceptions

from .. import group


@contextlib.contextmanager
def fail_then_delay(seconds=5):
    try:
        yield
    except requests.exceptions.ConnectionError:
        gevent.sleep(seconds)


class Worker(object):
    """The worker be used to kick us."""

    logger = logging.getLogger(__name__).getChild("Worker")

    def __init__(self, group, queue_size=10):
        self.group = group
        self.members_queue = gevent.queue.Queue(queue_size)

    def produce(self):
        while True:
            with fail_then_delay():
                for member in self.group.members():
                    self.members_queue.put(member)
                    self.logger.info(u"%s will be kicked." % member.uid)
                else:
                    #: TODO adjust sleeping interval dynamically
                    self.logger.info(u"Now have a rest, sleep 30 seconds.")
                    gevent.sleep(30)

    def consume(self):
        while True:
            with fail_then_delay():
                member = self.members_queue.get()
                member.kick()
                self.logger.info(u"%s has been kicked." % member.uid)
                gevent.sleep(1)

    def join(self):
        self.logger.info(u"The worker start working.")
        jobs = [gevent.spawn(self.produce), gevent.spawn(self.consume)]
        gevent.joinall(jobs)
