.. _commands:

Commands
========

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


Options
^^^^^^^

 - ``--indent``: Specifies the indent level to use when pretty-printing output.
   Example: ``./manage.py dumpdata --indent=4``
 - ``--filter``: Type of entries (new, spam, killed) that should be returned.
   Types can be combined by separating them with a comma. Example: 
   ``./manage.py dumpdata --filter=spam,killed``
 - ``--exclude``: Type of entries (new, spam, killed) that should be excluded.
   Types can be combined by separating them with a comma. Example: 
   ``./manage.py dumpdata --exclude=spam,killed``

disqus_export
-------------

disqus_threadedcomments_export
------------------------------

