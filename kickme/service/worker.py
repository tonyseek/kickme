import logging

import gevent
import gevent.queue

from .. import group


class Worker(object):
    """The worker be used to kick us."""

    logger = logging.getLogger(__name__).getChild("Worker")

    def __init__(self, group, queue_size=10):
        self.group = group
        self.members_queue = gevent.queue.Queue(queue_size)

    def produce(self):
        while True:
            for member in self.group.members():
                self.members_queue.put(member)
                self.logger.info(u"%s will be kicked." % member.uid)
            else:
                #: TODO adjust sleeping interval dynamically
                self.logger.info(u"Now have a rest, sleep 30 seconds.")
                gevent.sleep(30)

    def consume(self):
        while True:
            member = self.members_queue.get()
            member.kick()
            self.logger.info(u"%s has been kicked." % member.uid)
            gevent.sleep(1)

    def join(self):
        self.logger.info(u"The worker start working.")
        jobs = [gevent.spawn(self.produce), gevent.spawn(self.consume)]
        gevent.joinall(jobs)
