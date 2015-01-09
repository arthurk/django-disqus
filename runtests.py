#!/usr/bin/env python
import sys
from os.path import dirname, abspath

from django.conf import settings
from django.utils.version import get_version

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
    if get_version().split('.')[1] == '7':
        from django.apps import apps
        apps.populate(settings.INSTALLED_APPS)


from django.test.simple import DjangoTestSuiteRunner
test_runner = DjangoTestSuiteRunner(verbosity=1, interactive=True)


def runtests(*test_args):
    if not test_args:
        test_args = ['disqus']
    parent = dirname(abspath(__file__))
    sys.path.insert(0, parent)
    failures = test_runner.run_tests(test_args)
    sys.exit(failures)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
