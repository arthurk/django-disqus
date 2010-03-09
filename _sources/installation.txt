.. _installation:

Installation
============

The easiest way to get django-disqus is if you have pip_ installed::

	pip install django-disqus

Without pip, it's still pretty easy. Download the django-disqus.tar.gz file
from `django-disqus' PyPI page`_, untar it and run::

	python setup.py install

.. _django-disqus' PyPI page: http://pypi.python.org/pypi/django-disqus/
.. _pip: http://pip.openplans.org/

Configuring your Django installation
------------------------------------

First, add ``disqus`` to your ``INSTALLED_APPS``. You **don't** need to run 
``syncdb`` as there are no models provided.

Next, add ``DISQUS_API_KEY`` and ``DISQUS_WEBSITE_SHORTNAME`` to your settings.
You can `get your API key here`_ (you must be logged in on the DISQUS_
website). To see the shortname of your website, navigate to Settings->General
on the DISQUS_ website.

Example settings.py::

   INSTALLED_APPS = (
        ...
        'disqus',
    )

    DISQUS_API_KEY = 'FOOBARFOOBARFOOBARFOOBARFOOBARF'
    DISQUS_WEBSITE_SHORTNAME = 'foobar' 

.. _get your API key here: http://disqus.com/api/get_my_key/
.. _DISQUS: http://disqus.com
