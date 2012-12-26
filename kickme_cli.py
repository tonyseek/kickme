import sys
import getpass
import logging.config

from kickme.service.worker import Worker
from kickme.account import (DoubanSession, DoubanLoginRequireCaptcha,
                            DoubanLoginError)
from kickme.utils import bytes_to_image


def main():
    logging.config.fileConfig("kickme_cli_logging.ini")
    session = DoubanSession()
    try:
        email = raw_input("E-mail: ")
        password = getpass.getpass("Password: ")
        captcha_id, captcha_solution = None, None
        while True:
            try:
                session.login(email, password, captcha_id, captcha_solution)
            except DoubanLoginRequireCaptcha as e:
                bytes_to_image(e.captcha.captcha_bytes).show()
                captcha_id = e.captcha.captcha_id
                captcha_solution = raw_input("Captcha Solution: ")
            except DoubanLoginError as e:
                print >> sys.stderr, "Failed to login: %s" % ",".join(e.args)
                sys.exit(-1)
            else:
                break

        group_id = raw_input("Group ID: ")
        worker = Worker(session.group(group_id))
        worker.join()
    except KeyboardInterrupt:
        print >> sys.stderr, "\nQuit.\n"


if __name__ == "__main__":
    main()
