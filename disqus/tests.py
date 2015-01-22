import unittest
import json

from django.conf import settings
if not settings.configured:
    settings.configure()

from django.contrib.sites.models import Site
from django.test.utils import override_settings
from unittest import TestCase, mock

from disqus.api import DisqusClient, DisqusException
from django.utils.six.moves.urllib.error import URLError
from django.utils.six.moves.urllib.parse import parse_qs, urlparse
from django.template import Context, Template
from disqus.templatetags.disqus_tags import (set_disqus_developer,
                                             set_disqus_identifier,
                                             set_disqus_url,
                                             set_disqus_title,
                                             set_disqus_category_id,
                                             get_config,
                                             disqus_dev,
                                             disqus_sso,
                                             disqus_num_replies,
                                             disqus_recent_comments,
                                             disqus_show_comments
                                            )


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


class FakeAnonUser(mock.Mock):

    def is_anonymous(self):
        return True


class FakeUser(mock.Mock):

    id = '1'
    username = 'flin'
    email = 'test@test.com'

    def is_anonymous(self):
        return False


class DisqusTemplatetagsTest(TestCase):

    def setUp(self):
        self.real_sites_manager = Site.objects

        self.context = {
            'request': 'some_request',
            'disqus_developer': 'some_developer',
            'disqus_identifier': 'some_id',
            'disqus_url': '//bestsiteever.ten',
            'disqus_title': 'test title',
            'disqus_category_id': 'test category'
        }

    def tearDown(self):
        Site.objects = self.real_sites_manager

    # Note: this is not tag.
    def test_get_config(self):

        js = get_config(self.context)

        self.assertIn('var disqus_developer = "some_developer";', js)
        self.assertIn('var disqus_identifier = "some_id";', js)
        self.assertIn('var disqus_category_id = "test category";', js)

        self.assertNotIn('var request = "some_request";', js)

        self.assertEqual(len(js.split('\n')), 5)

    def test_set_disqus_developer(self):

        set_disqus_developer(self.context, 'Guido')

        self.assertEqual(self.context['disqus_developer'], 'Guido')

    def test_set_disqus_identifier(self):

        set_disqus_identifier(self.context, 'spam', 'ham', 'eggs')

        self.assertEqual(self.context['disqus_identifier'], 'spamhameggs')

    def test_set_disqus_url(self):

        set_disqus_url(self.context, 'spam', 'ham', 'eggs')

        self.assertEqual(self.context['disqus_url'], 'spamhameggs')

    def test_set_disqus_title(self):

        set_disqus_title(self.context, 'Holy Grail')

        self.assertEqual(self.context['disqus_title'], 'Holy Grail')

    def test_set_disqus_category_id(self):

        set_disqus_category_id(self.context, 'Monty Python')

        self.assertEqual(self.context['disqus_category_id'], 'Monty Python')

    @override_settings(DEBUG=True)
    def test_disqus_dev_sets_full_url(self):

        template = Template("""
                            {% load disqus_tags %}
                            {% disqus_dev %}
                            """
                            )

        test_domain = 'example.org'
        url_path = '/path/to/page'

        # mock out Site manager
        Site.objects = FakeSiteManager(test_domain, 'test')

        context = {'request': FakeRequest(path=url_path)}

        generated_html = template.render(Context(context))

        full_url = '//{}{}'.format(test_domain, url_path)

        self.assertIn(full_url, generated_html)
        self.assertIn('var disqus_developer = 1;', generated_html)
        self.assertEqual(disqus_dev(context), {'disqus_url': full_url})

    @override_settings(DEBUG=False)
    def test_disqus_dev_if_debug_is_false(self):

        template = Template("""
                            {% load disqus_tags %}
                            {% disqus_dev %}
                            """
                            )

        test_domain = 'example.org'
        url_path = '/path/to/page'
        context = {'request': FakeRequest(path=url_path)}

        Site.objects = FakeSiteManager(test_domain, 'test')

        generated_html = template.render(Context(context))

        full_url = '//{}{}'.format(test_domain, url_path)

        self.assertNotIn(full_url, generated_html)
        self.assertEqual(disqus_dev(context), {})

    @override_settings(DISQUS_SECRET_KEY=None, DISQUS_PUBLIC_KEY=True)
    def test_disqus_sso_if_there_is_no_secret_key(self):

        output = disqus_sso({})
        self.assertIn('You need to set DISQUS_SECRET_KEY before you can use SSO', output)

    @override_settings(DISQUS_PUBLIC_KEY=None, DISQUS_SECRET_KEY=None)
    def test_disqus_sso_if_there_is_no_public_key_and_no_secret_key(self):

        output = disqus_sso({})
        self.assertIn('You need to set DISQUS_SECRET_KEY before you can use SSO', output)

    @override_settings(DISQUS_PUBLIC_KEY=None, DISQUS_SECRET_KEY=True)
    def test_disqus_sso_if_there_is_no_public_key(self):

        output = disqus_sso({})
        self.assertIn('You need to set DISQUS_PUBLIC_KEY before you can use SSO', output)

    @override_settings(DISQUS_PUBLIC_KEY=True, DISQUS_SECRET_KEY=True)
    def test_disqus_sso_if_user_is_anonymous(self):

        context = {'user': FakeAnonUser()}

        output = disqus_sso(context)
        self.assertEqual(output, '')

    # TODO
    @override_settings(DISQUS_PUBLIC_KEY='a'*64, DISQUS_SECRET_KEY='b'*64)
    def test_disqus_sso_if_all_inner_tests_passed(self):

        context = {'user': FakeUser()}
        key = 'a'*64

        output = disqus_sso(context)

        self.assertIn('disqus_config', output)
        self.assertIn('remote_auth_s3', output)
        self.assertIn('api_key = "{}"'.format(key), output)

    def test_disqus_num_replies_without_settings(self):

        t1 = Template("{% load disqus_tags %} {% disqus_num_replies %}")
        t2 = Template("{% load disqus_tags %} {% disqus_num_replies 'foobar' %}")

        render1 = t1.render(Context({}))
        render2 = t2.render(Context(self.context))

        self.assertIn("var disqus_shortname = '';", render1)

        self.assertIn("var disqus_shortname = 'foobar';", render2)
        self.assertIn('var disqus_developer = "some_developer";', render2)
        self.assertIn('var disqus_url = "//bestsiteever.ten";', render2)

    @override_settings(DISQUS_WEBSITE_SHORTNAME='best_test_site_ever')
    def test_disqus_num_replies_with_settings(self):

        t1 = Template("{% load disqus_tags %} {% disqus_show_comments %}")
        t2 = Template("{% load disqus_tags %} {% disqus_show_comments 'foobar' %}")

        render1 = t1.render(Context({}))
        render2 = t2.render(Context(self.context))

        self.assertIn("var disqus_shortname = 'best_test_site_ever';", render1)
        self.assertNotIn("var disqus_shortname = 'foobar';", render1)

        self.assertIn("var disqus_shortname = 'best_test_site_ever';", render2)
        self.assertIn('var disqus_identifier = "some_id";', render2)
        self.assertIn('var disqus_title = "test title";', render2)

    def test_disqus_recent_comments_without_settings(self):

        t1 = Template("{% load disqus_tags %} {% disqus_recent_comments %}")
        t2 = Template("{% load disqus_tags %} \
                      {% disqus_recent_comments shortname='foobar' \
                      num_items=7 \
                      excerpt_length=400 \
                      hide_avatars=1 \
                      avatar_size=50 %}"
                    )

        render1 = t1.render(Context({}))
        render2 = t2.render(Context(self.context))

        self.assertIn("var disqus_shortname = '';", render1)
        self.assertIn("num_items=5", render1)
        self.assertIn("excerpt_length=200", render1)
        self.assertIn("hide_avatars=0", render1)
        self.assertIn("avatar_size=32", render1)

        self.assertIn("var disqus_shortname = 'foobar';", render2)
        self.assertIn("num_items=7", render2)
        self.assertIn("excerpt_length=400", render2)
        self.assertIn("hide_avatars=1", render2)
        self.assertIn("avatar_size=50", render2)

        self.assertIn('var disqus_category_id = "test category";', render2)
        self.assertIn('var disqus_url = "//bestsiteever.ten";', render2)

    @override_settings(DISQUS_WEBSITE_SHORTNAME='best_test_site_ever')
    def test_disqus_recent_comments_with_settings(self):

        t1 = Template("{% load disqus_tags %} {% disqus_recent_comments %}")
        t2 = Template("{% load disqus_tags %} \
                      {% disqus_recent_comments shortname='foobar' \
                      num_items=7 \
                      excerpt_length=400 \
                      hide_avatars=1 \
                      avatar_size=50 %}"
                    )

        render1 = t1.render(Context({}))
        render2 = t2.render(Context(self.context))

        self.assertIn("var disqus_shortname = 'best_test_site_ever';", render1)
        self.assertIn("num_items=5", render1)
        self.assertIn("excerpt_length=200", render1)
        self.assertIn("hide_avatars=0", render1)
        self.assertIn("avatar_size=32", render1)

        self.assertIn("var disqus_shortname = 'best_test_site_ever';", render2)
        self.assertIn("num_items=7", render2)
        self.assertIn("excerpt_length=400", render2)
        self.assertIn("hide_avatars=1", render2)
        self.assertIn("avatar_size=50", render2)

        self.assertIn('var disqus_category_id = "test category";', render2)
        self.assertIn('var disqus_url = "//bestsiteever.ten";', render2)

    def test_disqus_show_comments_without_settings(self):

        t1 = Template("{% load disqus_tags %} {% disqus_show_comments %}")
        t2 = Template("{% load disqus_tags %} {% disqus_show_comments 'foobar' %}")

        render1 = t1.render(Context({}))
        render2 = t2.render(Context(self.context))

        self.assertIn("var disqus_shortname = '';", render1)

        self.assertIn("var disqus_shortname = 'foobar';", render2)
        self.assertIn('var disqus_developer = "some_developer";', render2)
        self.assertIn('var disqus_url = "//bestsiteever.ten";', render2)

    @override_settings(DISQUS_WEBSITE_SHORTNAME='best_test_site_ever')
    def test_disqus_show_comments_with_settings(self):

        t1 = Template("{% load disqus_tags %} {% disqus_show_comments %}")
        t2 = Template("{% load disqus_tags %} {% disqus_show_comments 'foobar' %}")

        render1 = t1.render(Context({}))
        render2 = t2.render(Context(self.context))

        self.assertIn("var disqus_shortname = 'best_test_site_ever';", render1)
        self.assertNotIn("var disqus_shortname = 'foobar';", render1)

        self.assertIn("var disqus_shortname = 'best_test_site_ever';", render2)
        self.assertIn('var disqus_identifier = "some_id";', render2)
        self.assertIn('var disqus_title = "test title";', render2)


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

            with self.assertRaises(TypeError):
                # str is not callable
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
