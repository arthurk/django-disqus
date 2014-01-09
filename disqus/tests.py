import unittest

from django.conf import settings
from django.core.management.base import CommandError
from unittest import TestCase

from disqus.api import DisqusClient

class DisqusTest(TestCase):
    def test_client_init(self):
        """
        First, we test if the DisqusClient class can be initialized
        and parameters that were passed are set correctly.
        """

        c = DisqusClient(foo='bar', bar='foo')
        self.assertEqual('bar', c.foo)
        self.assertEqual('foo', c.bar)
        with self.assertRaises(AttributeError):
            c.baz

if __name__ == '__main__':
    unittest.main()
