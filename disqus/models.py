import urllib, urllib2

from django.core.management.base import CommandError
from django.utils import simplejson as json

import unittest
from mock import Mock

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

class DisqusApiTests(unittest.TestCase):
    
    def setUp(self):
        self.api_key = 'foobar'
        self.forum_api_key = 'barfoo'
        self.forum_objects = [Forum(id=12345,
                                    name='Test 1',
                                    shortname='test1',
                                    created_at='2009-01-17 01:01:01.123456'),
                              Forum(id=98765,
                                    name='Test 2',
                                    shortname='test2',
                                    created_at='2009-01-20 15:15:15.205317'),]
        self.thread_objects = [Thread(id=12345678,
                                      forum=12345, 
                                      slug='man_bites_dog', 
                                      title='Man Bites Dog', 
                                      created_at='2009-01-20T21:38',
                                      allow_comments=True, 
                                      url='http://example.com/Man Bites Dog/', 
                                      hidden=False, 
                                      identifier='Man Bites Dog'),
                               Thread(id=98765432,
                                      forum=12345, 
                                      slug='john_smith', 
                                      title='John Smith', 
                                      created_at='2009-05-08T11:13',
                                      allow_comments=True, 
                                      url='http://example.com/John/',
                                      hidden=False, 
                                      identifier='John Smith'),]
        self.post_objects = [Post(id=123456,
                                  forum=12345,
                                  thread=12345,
                                  created_at='2009-01-20T13:20',
                                  message='Hi!',
                                  shown=True,
                                  points=0,
                                  is_anonymous=True, 
                                  anonymous_author=AnonymousAuthor(
                                        email_hash='556f4ac7e166daeedb1b8968e228480b',
                                        name='nobody',
                                        url='http://example.com/')),
                             Post(id=123457,
                                  forum=12345,
                                  thread=12345,
                                  created_at='2009-01-20T13:20',
                                  message='First!',
                                  shown=True,
                                  points=0,
                                  is_anonymous=True, 
                                  anonymous_author=AnonymousAuthor(
                                        email_hash='5bc9a086127610a13283cdf5a3aba574',
                                        name='Joe Somebody',
                                        url='http://example.com/')),]
                               
    def test_get_forum_list(self):
        disqus = DisqusApi(api_key=self.api_key)
        mock = Mock(return_value=[
            {u'created_at': u'2009-01-17 01:01:01.123456', 
             u'shortname': u'test1', 
             u'name': u'Test 1', 
             u'id': u'12345'}, 
            {u'created_at': u'2009-01-20 15:15:15.205317', 
             u'shortname': u'test2', 
             u'name': u'Test 2', 
             u'id': u'98765'}])
        disqus.call = mock
        forum_list = disqus.get_forum_list()
        for count, forum in enumerate(forum_list):
            self.assertEqual(forum.id, self.forum_objects[count].id)
            self.assertEqual(forum.shortname, self.forum_objects[count].shortname)
            self.assertEqual(forum.name, self.forum_objects[count].name)
            self.assertEqual(forum.created_at, self.forum_objects[count].created_at)
        disqus.call.assert_called_with('get_forum_list', 
                                       {'user_api_key': self.api_key})
    
    def test_get_forum_api_key(self):
        """Test that a forums api key is returned"""
        disqus = DisqusApi(api_key=self.api_key)
        disqus.call = Mock(return_value=self.forum_api_key)
        forum_api_key = disqus.get_forum_api_key(self.forum_objects[0])
        disqus.call.assert_called_with('get_forum_api_key', 
                                       {'user_api_key': self.api_key, 
                                        'forum_id': self.forum_objects[0].id})
        self.assertEqual(forum_api_key, self.forum_api_key)
    
    def test_get_thread_list(self):
        """Test that get_thread_list returns a list of Thread objects"""       
        disqus = DisqusApi(api_key=self.api_key)
        disqus.call = Mock(return_value=[{
                            u'allow_comments': True,
                            u'created_at': u'2009-01-20T21:38',
                            u'forum': u'12345',
                            u'hidden': False,
                            u'id': u'12345678',
                            u'identifier': u'Man Bites Dog',
                            u'slug': u'man_bites_dog',
                            u'title': u'Man Bites Dog',
                            u'url': u'http://example.com/Man Bites Dog/'},
                            {u'allow_comments': True,
                            u'created_at': u'2009-05-08T11:13',
                            u'forum': u'12345',
                            u'hidden': False,
                            u'id': u'98765432',
                            u'identifier': u'John Smith',
                            u'slug': u'john_smith',
                            u'title': u'John Smith',
                            u'url': u'http://example.com/John/'},])
        threads = disqus.get_thread_list(forum_api_key=self.forum_api_key)
        for count, thread in enumerate(threads):
            self.assertEqual(thread.id, self.thread_objects[count].id)
            self.assertEqual(thread.forum, self.thread_objects[count].forum)
            self.assertEqual(thread.slug, self.thread_objects[count].slug)
            self.assertEqual(thread.title, self.thread_objects[count].title)
            self.assertEqual(thread.created_at, self.thread_objects[count].created_at)
            self.assertEqual(thread.allow_comments, self.thread_objects[count].allow_comments)
            self.assertEqual(thread.url, self.thread_objects[count].url)
            self.assertEqual(thread.hidden, self.thread_objects[count].hidden)
            self.assertEqual(thread.identifier, self.thread_objects[count].identifier)
        disqus.call.assert_called_with('get_thread_list', 
                                       {'forum_api_key': self.forum_api_key})
    
    def test_get_thread_posts(self):
        disqus = DisqusApi(api_key=self.api_key)
        disqus.call = Mock(return_value=[
            {u'anonymous_author': {u'email_hash': u'556f4ac7e166daeedb1b8968e228480b',
                                   u'name': u'nobody',
                                   u'url': u'http://example.com/~frank/'},
             u'created_at': u'2009-01-20T13:20',
             u'forum': u'12345',
             u'id': u'123456',
             u'is_anonymous': True,
             u'message': u'Hi!',
             u'parent_post': None,
             u'points': 0,
             u'shown': True,
             u'thread': u'12345'},
            {u'anonymous_author': {u'email_hash': u'5bc9a086127610a13283cdf5a3aba574',
                                   u'name': u'Joe Somebody',
                                   u'url': u'http://example.com/~joe/'},
             u'created_at': u'2009-01-20T13:20',
             u'forum': u'12345',
             u'id': u'123457',
             u'is_anonymous': True,
             u'message': u'First!',
             u'parent_post': None,
             u'points': 0,
             u'shown': True,
             u'thread': u'12345'},])
        posts = disqus.get_thread_posts(forum_api_key=self.forum_api_key,
                                        thread=self.thread_objects[0])
        for count, post in enumerate(posts):
            self.assertEqual(post.id, self.post_objects[count].id)
            self.assertEqual(post.forum, self.post_objects[count].forum)
            self.assertEqual(post.thread, self.post_objects[count].thread)
            self.assertEqual(post.created_at, self.post_objects[count].created_at)
            self.assertEqual(post.message, self.post_objects[count].message)
            self.assertEqual(post.shown, self.post_objects[count].shown)
            self.assertEqual(post.is_anonymous, self.post_objects[count].is_anonymous)
            self.assertEqual(post.anonymous_author, self.post_objects[count].anonymous_author)
            self.assertEqual(post.author, self.post_objects[count].author)
            self.assertEqual(post.parent_post, self.post_objects[count].parent_post)
        disqus.call.assert_called_with('get_thread_posts', 
                                       {'forum_api_key': self.forum_api_key,
                                        'thread_id': self.thread_objects[0].id})
        
if __name__ == '__main__':
    unittest.main()

