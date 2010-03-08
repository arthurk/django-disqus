from urllib import urlencode
import urllib2

from django.utils import simplejson as json

# A custom ProxyHandler for the urllib2 module that will not
# auto-detect proxy settings
proxy_support = urllib2.ProxyHandler({})
opener = urllib2.build_opener(proxy_support)
urllib2.install_opener(opener)

class DisqusException(Exception):
    """Exception raised for errors with the DISQUS API."""
    pass

class DisqusClient(object):
    """
    Client for the DISQUS API.

    Example:
        >>> client = DisqusClient()
        >>> json = client.get_forum_list(user_api_key=DISQUS_API_KEY)
    """
    METHODS = {
        'create_post': 'POST',
        'get_forum_api_key': 'GET',
        'get_forum_list': 'GET',
        'get_forum_posts': 'GET',
        'get_num_posts': 'GET',
        'get_thread_by_url': 'GET',
        'get_thread_list': 'GET',
        'get_thread_posts': 'GET',
        'get_updated_threads': 'GET',
        'get_user_name': 'POST',
        'moderate_post': 'POST',
        'thread_by_identifier': 'POST',
        'update_thread': 'POST',
    }

    def __init__(self, **kwargs):
        self.api_url = 'http://disqus.com/api/%s/?api_version=1.1'
        self.__dict__.update(kwargs)

    def __getattr__(self, attr):
        """
        Called when an attribute is not found in the usual places
        (__dict__, class tree) this method will check if the attribute
        name is a DISQUS API method and call the `call` method.
        If it isn't in the METHODS dict, it will raise an AttributeError.
        """
        if attr in self.METHODS:
            def call_method(**kwargs):
                return self.call(attr, **kwargs)
            return call_method
        raise AttributeError

    def _get_request(self, request_url, request_method, **params):
        """
        Return a urllib2.Request object that has the GET parameters
        attached to the url or the POST data attached to the object.
        """
        if request_method == 'GET':
            if params:
                request_url += '&%s' % urlencode(params)
            request = urllib2.Request(request_url)
        elif request_method == 'POST':
            request = urllib2.Request(request_url, urlencode(params))
        return request

    def call(self, method, **params):
        """
        Call the DISQUS API and return the json response.
        URLError is raised when the request failed.
        DisqusException is raised when the query didn't succeed.
        """
        url = self.api_url % method
        request = self._get_request(url, self.METHODS[method], **params)
        try:
            response = urllib2.urlopen(request)
        except urllib2.URLError, e:
            raise
        else:
            response_json = json.loads(response.read())
            if not response_json['succeeded']:
                raise DisqusException(response_json['message'])
            return response_json['message']
