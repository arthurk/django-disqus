.. _templatetags:

Templatetags
============

Before you can use the template tags, you need to load them with
``{% load disqus_tags %}``.

disqus_dev
----------

Return the HTML/Javascript code to enable DISQUS comments on a local
development server. This template tag will only return a value
if the ``settings.DEBUG`` setting is set to ``True``. If you don't
include this, the comment form will not show up on a local development server.

Example::

    {% load disqus_tags %}
    {% disqus_dev %}

Result::
    
    <script type="text/javascript">
      var disqus_developer = 1;
      var disqus_url = 'http://arthurkoziel.com/';
    </script>

disqus_show_comments
--------------------

Return the HTML code to display DISQUS comments. This includes
the comments for the current Thread and the comment form.

Example::

    {% load disqus_tags %}
    {% disqus_show_comments %}

Result::
    
    <div id="disqus_thread"></div>
    <script type="text/javascript" src="http://disqus.com/forums/arthurkozielsblog/embed.js"></script>
    <noscript><p><a href="http://arthurkozielsblog.disqus.com/?url=ref">View the discussion thread.</a></p></noscript>
    <p><a href="http://disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a></p>

**Options**:

 - ``shortname``: DISQUS website shortname that should be used. The
   ``settings.DISQUS_WEBSITE_SHORTNAME`` setting takes precedence
   over this parameter. Example: ``{% disqus_show_comments "foobar" %}``

disqus_num_replies
------------------

Return the HTML/Javascript code that transforms links which end with an
``#disqus_thread`` anchor into the thread's comment count.

Example::

    {% load disqus_tags %}
    <a href="{{ object.get_absolute_url }}#disqus_thread">View Comments</a>
    {% disqus_num_replies %}

Template Tag output::
    
    <script type="text/javascript">
    ...
    </script>

The javascript will then transform the link to::

    <a href="foobar/">2 Comments</a>

**Options**:

 - ``shortname``: DISQUS website shortname that should be used. The 
   ``settings.DISQUS_WEBSITE_SHORTNAME`` setting takes precedence over this
   parameter. Example: ``{% disqus_num_replies "foobar" %}``
