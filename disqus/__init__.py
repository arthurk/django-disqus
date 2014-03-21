try:
    import urllib2  # compat with py2
    urlopen = urllib2.urlopen
except ImportError:
    import urllib  # compat with py3
    urlopen = urllib.request.urlopen

from django.core.management.base import CommandError
from django.utils import simplejson as json


def call(method, data, post=False):
    """
    Calls `method` from the DISQUS API with data either in POST or GET.
    Returns deserialized JSON response.
    """
    url = "%s%s" % ('http://disqus.com/api/', method)
    if post:
        # POST request
        url += "/"
        data = urllib.urlencode(data)
    else:
        # GET request
        url += "?%s" % urllib.urlencode(data)
        data = ''
    res = json.load(urlopen(url, data))
    if not res['succeeded']:
        raise CommandError("'%s' failed: %s\nData: %s" % (method, res['code'], data))
    return res['message']
