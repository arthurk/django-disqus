import urllib, urllib2

from django.core.management.base import CommandError
from django.utils import simplejson as json

class Forum(object):
    def __init__(self, id, shortname, name, created_at):
        self.id = int(id)
        self.shortname = shortname
        self.name = name
        self.created_at = created_at
    
    def __repr__(self):
        return "<Forum %s>" % self.id

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False
    
class Thread(object):
    def __init__(self, id, forum, slug, title, created_at, allow_comments, 
                 url, hidden=False, identifier=None):
        self.id = int(id)
        self.forum = int(forum)
        self.slug = slug
        self.title = title
        self.created_at = created_at
        self.allow_comments = bool(allow_comments)
        self.url = url
        self.hidden = bool(hidden)
        self.identifier = identifier
    
    def __repr__(self):
        return "<Thread %s>" % self.id
    
    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

class Post(object):
    def __init__(self, id, forum, thread, created_at, message, shown, points,
                 is_anonymous, anonymous_author=None, author=None, 
                 parent_post=None):
        self.id = int(id)
        self.forum = int(forum)
        self.thread = int(thread)
        self.created_at = created_at
        self.message = message
        self.parent_post = parent_post
        self.shown = shown
        self.is_anonymous = bool(is_anonymous)
        self.anonymous_author = anonymous_author
        self.author = author

    def __repr__(self):
        return "<Post %s>" % self.id

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

class AnonymousAuthor(object):
    def __init__(self, name, url, email_hash):
        self.name = name
        self.url = url
        self.email_hash = email_hash
    
    def __eq__(self, other):
        if self.email_hash == other.email_hash:
            return True
        return False
        
class Author(object):
    def __init__(self, id, username, display_name, url, email_hash, has_avatar):
        self.id = int(id)
        self.username = username
        self.display_name = display_name
        self.url = url
        self.email_hash = email_hash
        self.has_avatar = has_avatar

    def __repr__(self):
        return "<Author %s; %s>" % (self.id, self.username)

    def __eq__(self, other):
        if self.id == other.id:
            return True
        return False

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
            raise CommandError("'%s' failed: %s\nData: %s" % (method, 
                                                              res['code'],
                                                              data))
        return res['message']
    
    def get_forum_list(self):
        """Returns a list of `Forum` objects associated with an API key"""
        return [Forum(id=f['id'],
                      shortname=f['shortname'], 
                      name=f['name'], 
                      created_at=f['created_at']) 
                for f in self.call('get_forum_list', 
                                   {'user_api_key': self.api_key})]
    
    def get_forum_api_key(self, forum):
        """Returns the forum API key for a `Forum`"""
        return self.call('get_forum_api_key', {'user_api_key': self.api_key, 
                                                'forum_id': forum.id})
    
    def get_thread_list(self, forum_api_key):
        """Returns a list of `Thread` objects associated with an forum API key"""
        return [Thread(id=t['id'], 
                       allow_comments=t['allow_comments'], 
                       created_at=t['created_at'],
                       forum=t['forum'],
                       hidden=t['hidden'], 
                       identifier=t['identifier'], 
                       slug=t['slug'], 
                       title=t['title'], 
                       url=t['url']) 
                for t in self.call('get_thread_list', 
                                   {'forum_api_key': forum_api_key})]
    
    def get_thread_posts(self, forum_api_key, thread):
        """Returns a list of `Thread` objects associated with an forum API key"""
        posts = []
        for post in self.call('get_thread_posts', {'forum_api_key': forum_api_key,
                                                'thread_id': thread.id}):
            if post['is_anonymous']:
                anonymous_author = AnonymousAuthor(name=post['anonymous_author']['name'],
                                                   url=post['anonymous_author']['url'],
                                                   email_hash=post['anonymous_author']['email_hash'])
                author = None
            else:
                author = Author(id=post['author']['id'],
                                username=post['author']['username'],
                                display_name=post['author']['display_name'],
                                url=post['author']['url'],
                                email_hash=post['author']['email_hash'],
                                has_avatar=post['author']['has_avatar'])
                anonymous_author = None
            
            posts.append(Post(id=post['id'], 
                              forum=post['forum'], 
                              thread=post['thread'],
                              created_at=post['created_at'],
                              message=post['message'], 
                              shown=post['shown'], 
                              points=post['points'], 
                              is_anonymous=post['is_anonymous'], 
                              anonymous_author=anonymous_author,
                              author=author,
                              parent_post=post['parent_post'],))
        return posts
