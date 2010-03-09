from django.conf import settings
from django.core.management.base import CommandError

from disqus.api import DisqusClient

__test__ = {'API_TESTS': """

First, we test if the DisqusClient class can be initialized
and parameters that were passed are set correctly.

>>> c = DisqusClient(foo='bar', bar='foo')
>>> c.foo
'bar'
>>> c.bar
'foo'
>>> c.baz
Traceback (most recent call last):
    ...
AttributeError


When a DISQUS API method is called, the call method should be used.

>>> c.get_forum_list
<function call_method at ...>
""",
}

