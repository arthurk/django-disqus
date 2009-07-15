import urllib, urllib2

from django.core.management.base import CommandError
from django.utils import simplejson as json

class Forum(object):
    def __init__(self, id, shortname, name, created_at):
        self.id = id
        self.shortname = shortname
        self.name = name
        self.created_at = created_at
        
class Thread(object):
    def __init__(self, id, forum, slug, title, created_at, allow_comments, url):
        self.id = id
        self.forum = forum
        self.slug = slug
        self.title = title
        self.created_at = created_at
        self.allow_comments = allow_comments
        self.url = url

class Post(object):
    def __init__(self, id, forum, thread, created_at, message, parent_post, shown, is_anonymous, anonymous_author, author):
        self.id = id
        self.forum = forum
        self.thread = thread
        self.created_at = created_at
        self.message = message
        self.parent_post = parent_post
        self.shown = shown
        self.is_anonymous = is_anonymous
        self.anonymous_author = anonymous_author
        self.author = author

class DisqusApi(object):
    API_URL = 'http://disqus.com/api/'
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def call(self, method, data, post=False):
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
        res = json.load(urllib2.urlopen(url, data))
        if not res['succeeded']:
            raise CommandError("'%s' failed: %s\nData: %s" % (method, res['code'], data))
        return res['message']
    
    def get_forum_list(self):        
        return [Forum(f['id'], f['shortname'], f['name'], f['created_at']) 
                for f in self.call('get_forum_list', {'user_api_key': self.api_key})]
    
    def get_forum_api_key(self, forum):
         return self.call('get_forum_api_key', {'user_api_key': self.api_key, 'forum_id': forum.id})