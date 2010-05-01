#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-disqus',
    version='0.3.1',
    description='Export existing comments to and integrate DISQUS into your Django website',
    author='Arthur Koziel',
    author_email='arthur@arthurkoziel.com',
    url='http://arthurk.github.com/django-disqus/',
    license='New BSD License',
    classifiers=[
      'Framework :: Django',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python',
    ],
    packages=find_packages(),
    zip_safe=False,
)
