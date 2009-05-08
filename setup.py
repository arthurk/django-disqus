#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-disqus',
    version='0.1',
    description='Easily integrate DISQUS comments into your Django website',
    author='Arthur Koziel',
    author_email='arthur@arthurkoziel.com',
    url='http://github.com/arthurk/django-disqus',
    license='New BSD License',
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Environment :: Plugins',
      'Framework :: Django',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python',
      'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(),
    zip_safe=False,
)
