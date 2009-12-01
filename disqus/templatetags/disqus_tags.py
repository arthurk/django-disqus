from django import template
from django.template.defaultfilters import escapejs
from django.conf import settings
from django.contrib.sites.models import Site

register = template.Library()

def disqus_dev():
    """
    Returns the HTML/js code to enable DISQUS comments on a local 
    development server if the settings.DEBUG is set to True.
    """
    if settings.DEBUG:
        return """
        <script type="text/javascript">
          var disqus_developer = 1;
          var disqus_url = 'http://%s/';
        </script>
        """ % Site.objects.get_current().domain
    return ""

def disqus_num_replies(shortname=''):
    """
    Returns the HTML/js code necessary to display the number of comments
    for a DISQUS thread.
    """
    if not shortname:
        shortname = settings.DISQUS_WEBSITE_SHORTNAME
    return """
    <script type="text/javascript">
    //<![CDATA[
    (function() {
        var links = document.getElementsByTagName('a');
        var query = '?';
        for(var i = 0; i < links.length; i++) {
            if(links[i].href.indexOf('#disqus_thread') >= 0) {
                query += 'url' + i + '=' + encodeURIComponent(links[i].href) + '&';
            }
        }
        document.write('<script type="text/javascript" src="http://disqus.com/forums/%s/get_num_replies.js' + query + '"></' + 'script>');
    })();
    //]]>
    </script>
    """ % shortname

def disqus_show_comments(title=None, url=None, snippet=None, shortname=''):
    """
    Returns the HTML code necessary to display DISQUS comments.
    """
    if not shortname:
        shortname = settings.DISQUS_WEBSITE_SHORTNAME
    if title or url or snippet:
        s = '<script type="text/javascript">'
        if title:
            s += 'var disqus_title = "%s";' % escapejs(title)
        if url:
            s += 'var disqus_url = "http://%s%s";' % \
                (Site.objects.get_current().domain, escapejs(url))
        if snippet:
            s += 'var disqus_message = "%s";' % escapejs(snippet)
        s += '</script>'
    else:
        s = ''
    return s + """
    <div id="disqus_thread"></div>
    <script type="text/javascript" src="http://disqus.com/forums/%(shortname)s/embed.js"></script>
    <noscript><p><a href="http://%(shortname)s.disqus.com/?url=ref">View the discussion thread.</a></p></noscript>
    <p><a href="http://disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a></p>
    """ % dict(shortname=shortname)

def disqus_recent_comments(num_items=3, avatar_size=32, shortname=''):
    """
    Returns the HTML/js code necessary to display the recent comments widget.
    """
    if not shortname:
        shortname = settings.DISQUS_WEBSITE_SHORTNAME
    return """
    <script type="text/javascript" src="http://disqus.com/forums/%(shortname)s/recent_comments_widget.js?num_items=%(num_items)d&amp;avatar_size=%(avatar_size)d"></script>
    <noscript><p><a href="http://%(shortname)s.disqus.com/?url=ref">View the discussion thread.</a></p></noscript>
    """ % dict(shortname=shortname,
               num_items=num_items,
               avatar_size=avatar_size)

def disqus_top_commenters(num_items=5, hide_mod=0, hide_avatars=0, avatar_size=32, shortname=''):
    """
    Returns the HTML/js code necessary to display top commenters
    """
    if not shortname:
        shortname = settings.DISQUS_WEBSITE_SHORTNAME
    return """
    <script type="text/javascript" src="http://disqus.com/forums/%(shortname)s/top_commenters_widget.js?num_items=%(num_items)d&hide_mods=%(hide_mod)d&hide_avatars=%(hide_avatars)d&avatar_size=%(avatar_size)d"></script>
    """ % dict(shortname=shortname,
               num_items=num_items,
               hide_mod=hide_mod,
               hide_avatars=hide_avatars,
               avatar_size=avatar_size)

def disqus_popular_threads(num_items=5, shortname=''):
    """
    Returns the HTML/js code necessary to display top commenters
    """
    if not shortname:
        shortname = settings.DISQUS_WEBSITE_SHORTNAME
    return """
    <script type="text/javascript" src="http://disqus.com/forums/%(shortname)s/popular_threads_widget.js?num_items=%(num_items)d"></script>
    """ % dict(shortname=shortname,
               num_items=num_items)

register.simple_tag(disqus_dev)
register.simple_tag(disqus_num_replies)
register.simple_tag(disqus_show_comments)
register.simple_tag(disqus_recent_comments)
register.simple_tag(disqus_top_commenters)
register.simple_tag(disqus_popular_threads)
