import collections

import requests
import lxml.html

from . import consts 


Captcha = collections.namedtuple("Captcha", ["captcha_id", "captcha_bytes"])


class DoubanSession(object):
    """The login session of douban account."""

    def __init__(self):
        self.client = requests.session()

    def login(self, username, password, captcha_id="", captcha_solution=""):
        """Sign an account in current session."""
        data = {"source": "index_nav", "redir": consts.HOME_URL,
                "form_email": username, "form_password": password,
                "user_login": consts.LOGIN_BTN_TEXT}
        if captcha_id and captcha_solution:
            data["source"] = "simple"
            data["captcha-id"] = captcha_id
            data["captcha-solution"] = captcha_solution

        r = self.client.post(consts.LOGIN_URL, data=data)
        etree = lxml.html.fromstring(r.text)

        #: require to provide captcha
        captcha_url = "".join(etree.xpath("//img[@id='captcha_image']/@src"))
        captcha_id = "".join(etree.xpath("//input[@name='captcha-id']/@value"))
        if captcha_url and captcha_id:
            captcha_bytes = self.client.get(captcha_url).content
            captcha = Captcha(captcha_id, captcha_bytes)
            raise DoubanLoginRequireCaptcha(captcha=captcha, username=username,
                                            password=password)

        #: errors occured
        errors = etree.xpath("//div[@id='item-error']/p/text()")
        if errors:
            raise DoubanLoginError(",".join(errors))


class DoubanLoginException(Exception):
    """The login has been interrupted."""


class DoubanLoginRequireCaptcha(DoubanLoginException):
    """Failed to login douban because of captcha is required."""

    def __init__(self, message=None, captcha=None, username=None,
                 password=None):
        super(DoubanLoginRequireCaptcha, self).__init__(message or "")
        self.captcha = captcha
        self.username = username
        self.password = password


class DoubanLoginError(DoubanLoginException):
    """Some errors occured while login."""
