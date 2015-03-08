import json

from django.utils.six.moves.urllib.parse import urlencode
from django.utils.six.moves.urllib.request import urlopen
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
    res = json.load(urlopen(url, data))
    if not res['succeeded']:
        raise CommandError("'%s' failed: %s\nData: %s" % (method, res['code'], data))
    return res['message']
