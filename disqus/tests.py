import unittest

from django.conf import settings
settings.configure()

from django.contrib.sites.models import Site
from django.core.management.base import CommandError
from django.test.utils import override_settings
from unittest import TestCase

from disqus.api import DisqusClient
from disqus.templatetags.disqus_tags import disqus_dev


class FakeRequest(object):
    def __init__(self, path):
        self.path = path


# mock Site
class FakeSiteManager(object):
    def __init__(self, domain, name):
        self.site = Site(domain=domain, name=name)
        
    def get_current(self):
        return self.site


class DisqusTest(TestCase):

    def setUp(self):
        self.real_sites_manager = Site.objects

    def tearDown(self):
        Site.objects = self.real_sites_manager

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

    def test_disqus_dev_sets_full_url(self):
        test_domain = 'example.org'
        url_path = '/path/to/page'
        full_url = 'http://%s%s' % (test_domain, url_path)
        context = {'request': FakeRequest(path=url_path)}
        # mock out Site manager
        Site.objects = FakeSiteManager(test_domain, 'test')
        with override_settings(DEBUG=True):
            generated_html = disqus_dev(context)
        self.assertIn(full_url, generated_html)

if __name__ == '__main__':
    unittest.main()
