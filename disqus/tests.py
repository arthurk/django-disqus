import unittest

from django.conf import settings
if not settings.configured:
    settings.configure()

from django.contrib.sites.models import Site
from django.test.utils import override_settings
from unittest import TestCase, mock

from disqus.api import DisqusClient
from disqus.templatetags.disqus_tags import disqus_dev
from django.utils.six.moves.urllib.error import URLError


class FakeRequest(object):

    def __init__(self, path):
        self.path = path


# mock Site
class FakeSiteManager(object):

    def __init__(self, domain, name):
        self.site = Site(domain=domain, name=name)

    def get_current(self):
        return self.site


class DisqusTemplatetagsTest(TestCase):

    def setUp(self):
        self.real_sites_manager = Site.objects

    def tearDown(self):
        Site.objects = self.real_sites_manager

    @override_settings(DEBUG=True)
    def test_disqus_dev_sets_full_url(self):
        test_domain = 'example.org'
        url_path = '/path/to/page'
        full_url = '//%s%s' % (test_domain, url_path)
        context = {'request': FakeRequest(path=url_path)}

        # mock out Site manager
        Site.objects = FakeSiteManager(test_domain, 'test')
        generated_html = disqus_dev(context)
        self.assertIn(full_url, generated_html)


class DisqusClientTest(TestCase):

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

    @mock.patch('disqus.api.DisqusClient.call')
    def test_client_call_call(self, call_mock):
        c = DisqusClient()

        attr = {'user_api_key': 'spam', 'developer_api_key': 'ham'}

        c.get_forum_api_key(**attr)
        call_mock.assert_called_with('get_forum_api_key', **attr)

    @mock.patch('disqus.api.DisqusClient._get_request')
    def test_client_get_request_call(self, _get_request_mock):
        c = DisqusClient()

        attr = {'user_api_key': 'spam', 'developer_api_key': 'ham'}

        url = c.api_url % 'get_forum_api_key'

        try:
            c.get_forum_api_key(**attr)
        except URLError:
            _get_request_mock.assert_called_with(
                url,
                c.METHODS['get_forum_api_key'],
                **attr)


if __name__ == '__main__':
    unittest.main()
