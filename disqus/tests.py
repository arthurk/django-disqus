from django.conf import settings
from disqus.api import DisqusClient
from mock import Mock
from disqus.management.commands import disqus_import
from disqus.models import Forum
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

"""}
