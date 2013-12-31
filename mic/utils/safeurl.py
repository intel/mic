"""
This module provides a class SafeURL which can contain url/user/password read
from config file, and hide plain user and password when it print to screen
"""
import os.path
import urllib
from urlparse import urlsplit, urlunsplit


def join_userpass(href, user, passwd):
    """Return authenticated URL with user and passwd embeded"""
    if not user and not passwd:
        return href

    if passwd:
        userpass = '%s:%s' % (urllib.quote(user, safe=''),
                              urllib.quote(passwd, safe=''))
    else:
        userpass = urllib.quote(user, safe='')

    parts = urlsplit(href)
    netloc = '%s@%s' % (userpass, parts[1])
    comps = list(parts)
    comps[1] = netloc
    return urlunsplit(comps)


def split_userpass(href):
    """Returns (href, user, passwd) of an authenticated URL"""
    parts = urlsplit(href)

    netloc = parts[1]
    if '@' not in netloc:
        return href, None, None

    userpass, netloc = netloc.split('@', 1)
    if ':' in userpass:
        user, passwd = [ urllib.unquote(i)
                           for i in userpass.split(':', 1) ]
    else:
        user, passwd = userpass, None

    comps = list(parts)
    comps[1] = netloc
    return urlunsplit(comps), user, passwd


class SafeURL(str):
    '''SafeURL can hide user info when it's printed to console.
    Use property full to get url with user info
    '''
    def __new__(cls, urlstring, user=None, passwd=None):
        """Imuutable object"""
        href, user1, passwd1 = split_userpass(urlstring)
        user = user if user else user1
        passwd = passwd if passwd else passwd1

        obj = super(SafeURL, cls).__new__(cls, href)
        obj.user = user
        obj.passwd = passwd
        obj.full = join_userpass(href, user, passwd)

        parts = urlsplit(href)
        obj.scheme = parts[0]
        obj.netloc = parts[1]
        obj.path = parts[2]
        obj.host = parts.hostname
        obj.port = parts.port
        return obj

    def join(self, *path):
        """Returns a new SafeURL with new path. Search part is removed since
        after join path is changed, keep the same search part is useless.
        """
        idx = self.full.find('?')
        url = self.full if idx < 0 else self.full[:idx]
        return SafeURL(os.path.join(url.rstrip('/'), *path))
