try:
    # Python 3
    from urllib.request import urlopen
    from urllib.parse import urlencode
except ImportError:
    # Python 2
    from urllib2 import urlopen
    from urllib import urlencode

from django.core.management.base import CommandError
from django.conf import settings
import json

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
