import json
try:
    from urllib.parse import urlencode
    import urllib.request as urllib2
except ImportError:
    from urllib import urlencode
    import urllib2

from django.core.management.base import CommandError


def call(method, data, post=False):
    """
    Calls `method` from the DISQUS API with data either in POST or GET.
    Returns deserialized JSON response.
    """
    url = "%s%s" % ('http://disqus.com/api/', method)
    if post:
        # POST request
        url += "/"
        data = urlencode(data)
    else:
        # GET request
        url += "?%s" % urlencode(data)
        data = ''
    res = json.load(urllib2.urlopen(url, data))
    if not res['succeeded']:
        raise CommandError(
            "'%s' failed: %s\nData: %s" % (method, res['code'], data))
    return res['message']
