.. _installation:

Installation
============

The easiest way to get django-disqus is if you have setuptools_ installed::

	easy_install django-disqus

Without setuptools, it's still pretty easy. Download the django-disqus.tgz file from 
`django-disqus's Cheeseshop page`_, untar it and run::

	python setup.py install

.. _django-disqus's Cheeseshop page: http://pypi.python.org/pypi/django-disqus/
.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall


Help and development
--------------------

If you'd like to help out, you can fork the project
at http://github.com/arthurk/django-disqus and report any bugs 
at http://github.com/arthurk/django-disqus/issues.

Configuring your Django installation
------------------------------------

Put 'disqus' in INSTALLED_APPS.
Add SHORTNAME...
