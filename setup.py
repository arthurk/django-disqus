#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django17-disqus',
    version='0.4.3',
    description='Export comments and integrate DISQUS into your Django website. Fix for Django 1.7. Thanks Arthur...',
    author='Alejandro Molina',
    author_email='jalemolina@gmail.com',
    url='https://github.com/jalemolina/django-disqus',
    license='New BSD License',
    classifiers=[
      'Framework :: Django',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python',
    ],
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
)
