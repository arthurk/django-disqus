django-disqus
=============

**WORK IN PROGRESS!**

Features
--------

    * Export comments from django.contrib.comments to DISQUS.
    * Dump data from DISQUS in local JSON file.

Requirements
------------

 * Django 1.0.2

Installation
------------

    1. Add 'django\_disqus' to your INSTALLED\_APPS.
    2. Add "DISQUS\_API\_KEY" and "DISQUS\_WEBSITE\_SHORTNAME" to your settings file. You can [http://disqus.com/api/get_my_key/][get your API key here].

Usage
-----

To export comments to disqus:

    python manage.py disqus-export

To dump the data from disqus:
    
    python manage.py disqus-dumpdata
    
You can pass the --indent option to specify the indentation of the output:
    
    python manage.py disqus-dumpdata --indent=4
    
Troubleshooting
---------------

Make sure that:

    * Each content object has a get\_absolute\_url() method.
    * Your Site has the correct domain set.
    * The content object has a __unicode__ method
