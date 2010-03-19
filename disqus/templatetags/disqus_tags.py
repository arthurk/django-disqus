from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.template.defaultfilters import escapejs

register = template.Library()

def disqus_dev():
    """
    Return the HTML/js code to enable DISQUS comments on a local
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
    Return the HTML/js code that transforms links that end with an
    #disqus_thread anchor into the thread's comment count.
    """
    shortname = getattr(settings, 'DISQUS_WEBSITE_SHORTNAME', shortname)
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

def disqus_show_comments(shortname=''):
    """
    Return the HTML code to display DISQUS comments.
    """
    shortname = getattr(settings, 'DISQUS_WEBSITE_SHORTNAME', shortname)
    return """
    <div id="disqus_thread"></div>
    <script type="text/javascript" async src="http://disqus.com/forums/%(shortname)s/embed.js"></script>
    <noscript><p><a href="http://%(shortname)s.disqus.com/?url=ref">View the discussion thread.</a></p></noscript>
    <p><a href="http://disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a></p>
    """ % dict(shortname=shortname)

register.simple_tag(disqus_dev)
register.simple_tag(disqus_num_replies)
register.simple_tag(disqus_show_comments)
