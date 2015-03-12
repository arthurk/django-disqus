.. _commands:

Commands
========

django-disqus provides the following management commands.

.. _disqus_dumpdata:

disqus_dumpdata
---------------

Outputs a list of comments in the JSON format.

If neither of the ``--filter`` or ``--exclude`` options are used, the output
will include approved, deleted and spam comments. Each comment will have the data
about its associated Author, Thread and Forum included.

Example output::

    [{
        "status": "approved", 
        "has_been_moderated": false, 
        "thread": {
            "category": "78805", 
            "allow_comments": true, 
            "forum": "71225", 
            "title": "Passing MEDIA_URL in Django&#39;s 500 error view", 
            "url": "http://arthurkoziel.com/2009/01/15/passing-mediaurl-djangos-500-error-view/", 
            "created_at": "2009-01-17T17:29", 
            "slug": "passing_media_url_in_django39s_500_error_view_arthur_koziels_blog", 
            "hidden": false, 
            "identifier": [], 
            "id": "102172011"
        }, 
        "forum": {
            "id": "71225", 
            "created_at": "2009-01-17 05:48:00.863075", 
            "shortname": "arthurkozielsblog", 
            "name": "Arthur Koziel\u2019s Blog", 
            "description": ""
        }, 
        "created_at": "2009-11-30T12:48", 
        "is_anonymous": true, 
        "points": 0, 
        "message": "Thanks for the article!", 
        "anonymous_author": {
            "url": "http://example.org/", 
            "email_hash": "j198m7123m12837m12893m7128121u23", 
            "name": "John", 
            "email": "john@example.org"
        }, 
        "ip_address": "12.345.678.11", 
        "id": "12345678", 
        "parent_post": null
    }]


**Options**:

 - ``--indent``: Specifies the indent level to use when pretty-printing output.
   Example: ``./manage.py disqus_dumpdata --indent=4``
 - ``--filter``: Type of entries (approved, spam, killed) that should be
   returned. Types can be combined by separating them with a comma. Example:
   ``./manage.py disqus_dumpdata --filter=spam,killed``
 - ``--exclude``: Type of entries (approved, spam, killed) that should be
   excluded. Types can be combined by separating them with a comma. Example:
   ``./manage.py disqus_dumpdata --exclude=spam,killed``

disqus_export
-------------

Export comments from contrib.comments to DISQUS.

Before you run this command, make sure that ``django.contrib.comments``
and ``django.contrib.sites`` are listed in your project's ``INSTALLED_APPS``.
You also need to change the domain of your Site from ``example.org`` to your
real domain.

The comment's associated content object must have the following two methods:

 - ``get_absolute_url``: Should return the URL of an object. For example: 
   ``/2009/10/10/foo``. This should not include the domain name
 - ``__unicode__``: Unicode representation of the object

The command will export all comments that have the ``is_public``
attribute set to ``True`` and ``is_removed`` set to ``False``. To test which
comments will be exported, you can pass the ``--dry-run`` option.

**Options**:

 - ``-d``/``--dry-run``: Does not export any comments, but merely outputs
   the comments which would have been exported. Example:
   ``./manage.py disqus_export --dry-run``
 - ``-v``/``--verbosity``: Specify the amount of information that should be
   printed to the console. A verbosity of ``0`` will output nothing. The
   default verbosity is ``1`` and print the title of the comments that are
   exported. Example: ``./manage.py disqus_export --verbosity=0``
 - ``-s``/``--state-file``: Specify the filepath where the export command
   should save its state (the id of the last exported comment) into.
   This makes it possible to resume interrupted exports.

