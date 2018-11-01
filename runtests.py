#!/usr/bin/env python
import logging
import sys
from os.path import dirname, abspath
from django.conf import settings
import django

if not settings.configured:
    settings.configure(
        DATABASE_ENGINE='sqlite3',
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.admin',
            'django.contrib.sessions',
            'django.contrib.contenttypes',
            'disqus',
        ],
        ROOT_URLCONF='',
        DEBUG=False,
    )


def runtests(*test_args):
    if not test_args:
        test_args = ['disqus']

    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)

    if django.VERSION < (1, 8):
        from django.test.simple import run_tests

        failures = run_tests(test_args, verbosity=1, interactive=True)
        sys.exit(failures)

    else:
        from django.test.runner import DiscoverRunner

        django.setup()
        runner = DiscoverRunner(verbosity=1, interactive=True)
        failures = runner.run_tests(test_args)
        sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
