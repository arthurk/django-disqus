Release Notes
=============

django-disqus 0.5 (08-MAR-2015)
---------------------------------

- Python 3.4 support
- Django 1.7 support
- Improved unit tests

Thanks a lot to `Alexey Kalinin <https://github.com/Alkalit>`_,
and also everyone else who submitted PR's regarding the
Django 1.7 support.

django-disqus 0.4.1 (19-APR-2011)
---------------------------------

- Fix installation on Windows (Bug #11)

django-disqus 0.4 (21-MAR-2011)
-------------------------------

- Fix for unicode titles in urlencode (http://bugs.python.org/issue1349732).
  Thanks `Adriano Petrich <https://github.com/frac>`_.
- New templatetags to set context variables:
    - set_disqus_developer
    - set_disqus_identifier
    - set_disqus_url
    - set_disqus_title
- Export comments as WXR feed

A huge thanks to `Corey Oordt <https://github.com/coordt>`_, who
implemented the new templatetags and the WXR feed.

django-disqus 0.3.4 (30-OCT-2010)
---------------------------------

- Update the `disqus_num_replies` template tag to use the new JS code.
  This will make the site load faster, as loading isn't blocked by the call to document.write.
  Thanks to Nick Fitzgerald.

django-disqus 0.3.3 (23-SEP-2010)
---------------------------------

- Update the `disqus_show_comments` template tag to use the new loader method.
  Thanks David Cramer for the patch.

django-disqus 0.3.2 (16-MAY-2010)
---------------------------------

- Added a `-s/--state-file` option to the :doc:`disqus_export </commands>`
  command. The state file saves the id of the last exported comment.
  This makes it possible to resume interrupted exports.
  Thanks `Horst Gutmann <http://zerokspot.com/>`_ for the patch.

django-disqus 0.3.1 (01-MAY-2010)
---------------------------------

This is a bugfix release. The following changes were made:

 - Fixed a bug where the disqus_export command raised an error if non-ascii
   characters were used in the author name.
 - Added "async" attribute to DISQUS JavaScript tag. This loads the comments
   faster on browsers that support the html5 async tag (e.g. firefox).

django-disqus 0.3 (09-MAR-2010)
-------------------------------

This release updates django-disqus to use the new DISQUS v1.1 API and
cleans up the templatetags and management commands.

**Management Commands**

The following management commands were renamed: 

 - ``disqus-dumpdata`` to ``disqus_dumpdata``
 - ``disqus-export`` to ``disqus_export``

The old names weren't valid Python module identifiers. This lead to
problems when trying to import them.

The ``disqus_dumpdata`` command has two new options:

 - ``filter``: Type of entries (e.g. spam or killed) that should be returned
 - ``exclude``: Type of entries that should be excluded from the response 

For further information take a look at the documentation for the 
:ref:`disqus_dumpdata` command.

The ``disqus-export-threadedcomments`` command was removed from django-disqus
because the upcoming ``django-threadedcomments`` release will rely on the
comment extension hooks provided in Django 1.1. This means that the 
``disqus_export`` command will work just fine when exporting threadedcomments.

**Templatetags**

The ``disqus_recent_comments`` templatetag was removed. If you want to use
this or any other widget, go to the *Tools* section on the DISQUS_ website.
There you can configure the widget and get the Javascript code that is 
necessary to display it on your website.

The parameters of the ``disqus_show_comments`` tag have changed. Previously
you could pass the title, url, snippet and shortname. As of this release,
it's only possible to pass the shortname. If you want to change the
Javascript variables that the DISQUS comment form uses, take a look at the
`Configure and override comment system behaviors`_ page in the DISQUS wiki.

.. _`Configure and override comment system behaviors`: http://help.disqus.com/entries/100880-configure-and-override-comment-system-behaviors
.. _DISQUS: http://disqus.com
