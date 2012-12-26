import json

from . import consts


class DoubanGroup(object):
    """The douban group service."""

    def __init__(self, client, session, group_id):
        self.client = client
        self.session = session
        self.group_id = group_id

    @property
    def group_id(self):
        return self._group_id

    @group_id.setter
    def group_id(self, value):
        self._group_id = value
        self._kick_url = consts.GROUP_KICK_URL.format(ck=self.session.ck,
                                                      uid="{uid}")
        self._mems_url = consts.GROUP_MEMBERS_API.format(gid=self.group_id)

    def members(self):
        r = self.client.get(self._mems_url)
        data = json.loads(r.text)
        members = [DoubanGroupMember(self.client, self, member_data)
                   for member_data in data["members"]]
        return members


class DoubanGroupMember(object):
    """The douban group's member management service."""

    def __init__(self, client, group, data):
        self.client = client
        self.group = group
        self.data = data

    #: assign getters of attributes
    _make_getter = lambda _attr: property(lambda self: self.data[_attr])
    for _attr in ("avatar", "alt", "id", "name", "uid"):
        locals()[_attr] = _make_getter(_attr)
    del _attr
    del _make_getter

    def kick(self):
        """Kick a member away current group."""
        r = self.client.get(self.group._kick_url.format(uid=self.uid),
                            allow_redirects=False)
        if r.status_code not in (200, 302):
            raise KickFailedError(r)


class DoubanGroupException(Exception):
    pass


class KickFailedError(DoubanGroupException):
    """Failed to kick a group member."""
