import unittest

from mock import Mock
from disqus.models import DisqusApi, Forum, Thread, Post, AnonymousAuthor, Author

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
