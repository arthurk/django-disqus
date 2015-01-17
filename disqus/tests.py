import unittest
import json

from django.conf import settings
if not settings.configured:
    settings.configure()

from django.contrib.sites.models import Site
from django.test.utils import override_settings
from unittest import TestCase, mock

from disqus.api import DisqusClient, DisqusException
from disqus.templatetags.disqus_tags import disqus_dev
from django.utils.six.moves.urllib.error import URLError
from django.utils.six.moves.urllib.parse import parse_qs, urlparse


class FakeRequest(object):

    def __init__(self, path):
        self.path = path


# mock Site
class FakeSiteManager(object):

    def __init__(self, domain, name):
        self.site = Site(domain=domain, name=name)

    def get_current(self):
        return self.site


class FakeUrlopen(mock.Mock):

    def read(self, *args, **kwargs):
        return '''
                {
                "message": [
                    {
                    "created_at": "2007-07-31 17:44:00",
                    "shortname": "disqus",
                    "description":
                    "The official Disqus forum. [...]",

                    "id": "NN", "name": "DISQUS Blog and Forum"
                    },
                    {
                    "created_at": "2008-09-10 14:37:31.744838",
                    "shortname": "antonkovalyov",
                    "description": "",
                    "id": "NN",
                    "name": "Anton Kovalyov"
                    }
                ],
                "code": "ok",
                "succeeded": true
                }
            '''


class FakeUrlopenNegative(mock.Mock):

    def read(self, *args, **kwargs):
        return '{"message":"message content","succeeded":false}'


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

    def setUp(self):

        self.client = DisqusClient()
        self.attr = {'user_api_key': 'spam', 'developer_api_key': 'ham'}

    def test_init_properly(self):
        """
        First, we test if the DisqusClient class can be initialized
        and parameters that were passed are set correctly.
        """

        c = DisqusClient(foo='bar', bar='foo')

        self.assertEqual('bar', c.foo)
        self.assertEqual('foo', c.bar)
        with self.assertRaises(AttributeError):
            c.baz

    # XXX bug or feature?
    def test_init_if_passed_args_with_name_like_in_METHODS_api_methods_become_overrided(self):
        c = DisqusClient(**DisqusClient.METHODS)

        for api_method in DisqusClient.METHODS:

            # str is not callable
            with self.assertRaises(TypeError):
                getattr(c, api_method)()

    @mock.patch('disqus.api.DisqusClient.call')
    def test_call_method_is_triggered_by_api_methods_from_METHODS(self, call_mock):

        for method in DisqusClient.METHODS:

            call = getattr(self.client, method)
            call(**self.attr)

            call_mock.assert_called_with(method, **self.attr)

    @mock.patch('disqus.api.urlopen', new_callable=FakeUrlopen)
    @mock.patch('disqus.api.DisqusClient._get_request')
    def test__get_request_is_triggered_by_call_method(self, _get_request_mock, urlopen_mock):

        for method in DisqusClient.METHODS:
            url = self.client.api_url % method

            call = getattr(self.client, method)
            call(**self.attr)

            _get_request_mock.assert_called_with(url, self.client.METHODS[method], **self.attr)

    @mock.patch('disqus.api.urlopen', new_callable=FakeUrlopen)
    def test_call_method_if_requst_is_succeeded_returns_a_json_message(self, urlopen_mock):

        rest_response = '''
                {
                "message": [
                    {
                    "created_at": "2007-07-31 17:44:00",
                    "shortname": "disqus",
                    "description":
                    "The official Disqus forum. [...]",

                    "id": "NN", "name": "DISQUS Blog and Forum"
                    },
                    {
                    "created_at": "2008-09-10 14:37:31.744838",
                    "shortname": "antonkovalyov",
                    "description": "",
                    "id": "NN",
                    "name": "Anton Kovalyov"
                    }
                ],
                "code": "ok",
                "succeeded": true
                }
            '''

        response_json = json.loads(rest_response)
        message = response_json['message']

        response = self.client.get_forum_list(user_api_key='spam')

        self.assertEqual(response, message)

    @mock.patch('disqus.api.urlopen', new_callable=FakeUrlopenNegative)
    def test_call_method_if_requst_is_not_succeeded_raise_an_exception(self, urlopen_mock):

        with self.assertRaises(DisqusException):

            self.client.get_forum_list()

    @mock.patch('disqus.api.DisqusClient._get_request')
    def test_call_method_if_during_request_error_occurred_raise_an_exception(self, _get_request_mock):

        with self.assertRaises(URLError):
            self.client.create_post()

    def test__get_request_if_http_method_is_get_returns_a_get_request(self):

        attr_ = {'user_api_key': ['spam'], 'developer_api_key': ['ham'], 'api_version': ['1.1']}

        for api_method, http_method in DisqusClient.METHODS.items():
            if http_method == "GET":

                url = self.client.api_url % api_method

                request_params = self.client._get_request(url, http_method, **self.attr)
                request_no_params = self.client._get_request(url, http_method)

                self.assertEqual(request_params.host, 'disqus.com')
                self.assertEqual(request_no_params.host, 'disqus.com')

                # check actual request method
                self.assertEqual(request_params.get_method(), http_method)
                self.assertEqual(request_no_params.get_method(), http_method)

                # getting url's query string
                # since parameters passed to api_url from a dict, mean randomly
                url_parsed1 = urlparse(request_params.full_url)
                qs_params = parse_qs(url_parsed1.query)

                url_parsed2 = urlparse(request_no_params.full_url)
                qs_no_params = parse_qs(url_parsed2.query)

                self.assertEqual(qs_params, attr_)
                # hardcoded in api_url
                self.assertEqual(qs_no_params, {'api_version': ['1.1']})

    def test__get_request_if_http_method_is_post_returns_a_post_request(self):

        attr_ = {'user_api_key': ['spam'], 'developer_api_key': ['ham']}

        for api_method, http_method in DisqusClient.METHODS.items():
            if http_method == "POST":

                url = self.client.api_url % api_method

                request_params = self.client._get_request(url, http_method, **self.attr)
                request_no_params = self.client._get_request(url, http_method)

                self.assertEqual(request_params.host, 'disqus.com')
                self.assertEqual(request_no_params.host, 'disqus.com')

                self.assertEqual(request_params.get_method(), http_method)
                self.assertEqual(request_no_params.get_method(), http_method)

                qs_params = parse_qs(request_params.data)
                qs_no_params = parse_qs(request_no_params.data)

                self.assertEqual(qs_params, attr_)
                self.assertEqual(qs_no_params, {})

    # XXX maybe exception must be raised explicitly (DisqusException)
    def test__get_request_if_http_method_is_not_post_or_get_raise_an_exception(self):

        for api_method in DisqusClient.METHODS:
            url = self.client.api_url % api_method

            with self.assertRaises(UnboundLocalError):
                self.client._get_request(url, 'PUSH', **self.attr)
            with self.assertRaises(UnboundLocalError):
                self.client._get_request(url, 'PUSH')

    # XXX Don't know how to implement this and if should.
    def test_call_method_if_api_version_passed_as_method_argument(self):
        pass

if __name__ == '__main__':
    unittest.main()
