from django.conf import settings
from disqus.api import DisqusClient
from mock import Mock
from disqus.management.commands import disqus_import
from disqus.models import Forum, Thread, Post, Author, AnonymousAuthor
from django.core.management.base import CommandError
from urllib2 import URLError

# TODO: Test API (if post parameters are attached/GET)
__test__ = {'API_TESTS': """

Create a Mock for the get_forum_list api function.

>>> get_forum_list_mock = Mock()
>>> get_forum_list_mock.return_value = [
...     {u'id': u'01234', u'created_at': u'2009-01-17 05:48:00.863075',
...      u'shortname': u'arthurkozielsblog',
...      u'name': u'Arthur Koziel\u2019s Blog', u'description': u''},
...     {u'id': u'56789', u'created_at': u'2009-01-20 15:23:14.205317',
...      u'shortname': u'foobar', u'name': u'FooBar',
...      u'description': u''}]
>>> DisqusClient.get_forum_list = get_forum_list_mock

Run the import_forums command and check that it called the get_forum_list
API function and imported the Forums into the database.

>>> cmd = disqus_import.Command()
>>> cmd.import_forums(user_api_key="foo")
>>> DisqusClient.get_forum_list.called
True

>>> f1 = Forum.objects.get(id='01234')
>>> f1.id, f1.shortname
(u'01234', u'arthurkozielsblog')

>>> f2 = Forum.objects.get(id='56789')
>>> f2.id, f2.shortname
(u'56789', u'foobar')

Check that a CommandError exception is raised if the wrong "user_api_key"
was provided to the import_forums function. Disqus returns a 400 error
when a paramter is wrong, so we mock this behaviour.

>>> DisqusClient.get_forum_list.side_effect = URLError("400")
>>> cmd.import_forums(user_api_key="bar")
Traceback (most recent call last):
...
CommandError: Could not get forums. Check your "DISQUS_API_KEY" setting.

The get_forum function takes a shortname and returns a Forum object from
the database that matches the shortname. If no such object exists in the
database, a CommandError should be raised.

>>> f3 = cmd.get_forum('foobar')
>>> f3.id
u'56789'
>>> cmd.get_forum('tacocat')
Traceback (most recent call last):
...
CommandError: Could not find forum with shortname "tacocat". \
Check your "DISQUS_WEBSITE_SHORTNAME" setting.

Test importing threads. First, we mock the API response. Since the
import_threads method uses a while loop to fetch the results, we
make sure the first one returns the 3 needed results and subsequent
calls return an empty list.

>>> mock = Mock()
>>> return_value = [
... {u'category': {u'id': 80118, u'title': u'General'},
... u'allow_comments': True, u'forum': u'01234', u'title': u'Peter Jones',
... u'url': u'http://example.com/Peter/', u'created_at': u'2009-05-08T11:13',
... u'id': u'00000003', u'hidden': False, u'identifier': [u'Peter Jones'],
... u'slug': u'peter_jones'},
... {u'category': {u'id': 80118, u'title': u'General'},
... u'allow_comments': True, u'forum': u'01234', u'title': u'John Smith',
... u'url': u'http://example.com/John/', u'created_at': u'2009-05-08T11:13',
... u'id': u'00000002', u'hidden': False, u'identifier': [u'John Smith'],
... u'slug': u'john_smith'},
... {u'category': {u'id': 80118, u'title': u'General'},
... u'allow_comments': True, u'forum': u'01234', u'title': u'Man Bites Dog',
... u'url': u'http://example.com/Man Bites Dog/', u'id': u'00000001',
... u'created_at': u'2009-01-20T21:38', u'hidden': False,
... u'identifier': [u'Man Bites Dog'], u'slug': u'man_bites_dog'}]
>>> def side_effect(*args, **kwargs):
...     if mock.call_count > 1:
...         return []
...     else:
...         return return_value
>>> mock.side_effect = side_effect
>>> DisqusClient.get_thread_list = mock

Import threads and check if they appear in the database.

>>> cmd.import_threads("foo", f1)
>>> DisqusClient.get_thread_list.called
True

>>> Thread.objects.all()
[<Thread: Peter Jones>, <Thread: John Smith>, <Thread: Man Bites Dog>]

Test importing Posts for Thread "John Smith".

>>> t = Thread.objects.get(id='00000002')
>>> mock = Mock()
>>> return_value = [
... {u'status': u'approved', u'has_been_moderated': False,
...  u'thread': {u'allow_comments': True, u'forum': u'01234',
...              u'title': u'John Smith', u'url': u'http://example.com/John/',
...              u'created_at': u'2009-05-08T11:13', u'id': u'00000002',
...              u'hidden': False, u'identifier': [u'John Smith'],
...              u'slug': u'john_smith'},
...  u'forum': {u'id': u'01234', u'created_at': u'2009-01-20 15:23:14.205317',
...             u'shortname': u'foobar', u'name': u'FooBar',
...             u'description': u''},
...  u'created_at': u'2009-01-20T13:19', u'is_anonymous': True, u'points': 0,
...  u'message': u'First here, too!',
...  u'anonymous_author': {u'url': u'http://example.com/~joe/', 
...                        u'email_hash': u'5bc9a086127610a13283cdf5a3aba574',
...                        u'name': u'Joe Somebody',
...                        u'email': u'jsomebody@example.com'},
...  u'ip_address': u'255.255.255.255', u'id': u'0000001',
...  u'parent_post': None},
... {u'status': u'approved', u'has_been_moderated': False,
...  u'thread': {u'allow_comments': True, u'forum': u'01234',
...              u'title': u'John Smith', u'url': u'http://example.com/John/',
...              u'created_at': u'2009-05-08T11:13', u'id': u'00000002',
...              u'hidden': False, u'identifier': [u'John Smith'],
...              u'slug': u'john_smith'},
...  u'forum': {u'id': u'01234', u'created_at': u'2009-01-20 15:23:14.205317',
...             u'shortname': u'foobar', u'name': u'FooBar',
...             u'description': u''},
...  u'created_at': u'2009-01-20T13:19', u'is_anonymous': True, u'points': 0,
...  u'message': u'First here, too!',
...  u'anonymous_author': {u'url': u'http://example.com/~joe/',
...                        u'email_hash': u'5bc9a086127610a13283cdf5a3aba574',
...                        u'name': u'Joe Somebody', 
...                        u'email': u'jsomebody@example.com'},
...  u'ip_address': u'255.255.255.255', u'id': u'0000002', 
...  u'parent_post': None},
... {u'status': u'approved', u'has_been_moderated': False,
...  u'thread': {u'allow_comments': True, u'forum': u'01234',
...              u'title': u'John Smith', u'url': u'http://example.com/John/',
...              u'created_at': u'2009-05-08T11:13', u'id': u'00000002',
...              u'hidden': False, u'identifier': [u'John Smith'],
...              u'slug': u'john_smith'},
...  u'forum': {u'id': u'01234', u'created_at': u'2009-01-20 15:23:14.205317',
...             u'shortname': u'foobar', u'name': u'FooBar',
...             u'description': u''},
...  u'created_at': u'2009-01-20T13:19', u'is_anonymous': False, u'points': 0,
...  u'message': u'First here, too!',
...  u'author': {u'username': u'someauthor',
...              u'email_hash': u'5bc9a086127610a13283cdf5a3aba574',
...              u'display_name': u'', u'has_avatar': False,
...              u'url': u'', u'id': 0000001,
...              u'avatar': {
...                  u'small': u'http://media.disqus.com/images/noavatar32.png',
...                  u'large': u'http://media.disqus.com/images/noavatar128.png',
...                  u'medium': u'http://media.disqus.com/images/noavatar92.png'},
...              u'email': u'asdasdasd@example.com'},
...  u'ip_address': u'255.255.255.255', u'id': u'0000003',
...  u'parent_post': None}]
>>> def side_effect(*args, **kwargs):
...     if mock.call_count > 1:
...         return []
...     else:
...         return return_value
>>> mock.side_effect = side_effect
>>> DisqusClient.get_forum_posts = mock

>>> cmd.import_posts("foo", f1)
>>> DisqusClient.get_forum_posts.called
True

>>> Author.objects.count()
1
>>> AnonymousAuthor.objects.count()
2
>>> Post.objects.count()
3

"""}
