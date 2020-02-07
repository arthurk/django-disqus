#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='django-disqus',
    version='0.6',
    description='Export comments and integrate DISQUS into your Django website',
    author='Arthur Koziel',
    author_email='arthur@arthurkoziel.com',
    url='https://django-disqus.readthedocs.io',
    license='New BSD License',
    classifiers=[
      'Framework :: Django',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
      'Programming Language :: Python :: 3.2',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
      'Programming Language :: Python :: 3.6',
    ],
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
    'Django>=3.0.3',
    'mock>=4.0.1',
    'six>=1.14.0'
    ],
)
