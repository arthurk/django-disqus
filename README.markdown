django-disqus
=============

**WORK IN PROGRESS!**

Management commands for Django which:

    * Export django.contrib.comments to DISQUS.

Requirements
------------

Django 1.0.2
simplejson 2.0.7

Installation
------------

Put 'django\_disqus' into your 'INSTALLED_APPS'
Add "DISQUS\_API_KEY" to your settings. You can  [http://disqus.com/api/get_my_key/][get your API key here].
Add "DISQUS\_WEBSITE_SHORTNAME" to your settings.

Usage
-----

To export comments to disqus:

    python manage.py disqus-export
    
Options
-------

    -v = Output verbosity. 1=minimal, 2=normal.
    
Troubleshooting
---------------

Make sure that:

    * Each content object has a get\_absolute\_url() method.
    * Your Site has the correct domain set.
    * The content objects has a __unicode__ method
