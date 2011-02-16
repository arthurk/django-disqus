from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.functional import curry

register = template.Library()

class ContextSetterNode(template.Node):
    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = template.Variable(var_value)
    
    def render(self, context):
        try:
            var_value = self.var_value.resolve(context)
        except template.VariableDoesNotExist:
            var_value = self.var_value.var
        
        context[self.var_name] = var_value
        return ''

def generic_setter_compiler(var_name, name, node_class, parser, token):
    """
    Returns a ContextSetterNode.
    
    For calls like {% set_this_value "My Value" %}
    """
    bits = token.split_contents()
    if(len(bits) != 2):
        message = "%s takes one argument" % name
        raise TemplateSyntaxError(message)
    return node_class(var_name, bits[1])

# Set the disqus_developer variable to 0/1. Default is 0
set_disqus_developer = curry(generic_setter_compiler, 'disqus_developer', 'set_disqus_developer', ContextSetterNode)

# Set the disqus_identifier variable to some unique value. Defaults to page's URL
set_disqus_identifier = curry(generic_setter_compiler, 'disqus_identifier', 'set_disqus_identifier', ContextSetterNode)

# Set the disqus_url variable to some value. Defaults to page's location
set_disqus_url = curry(generic_setter_compiler, 'disqus_url', 'set_disqus_url', ContextSetterNode)

# Set the disqus_title variable to some value. Defaults to page's title or URL
set_disqus_title = curry(generic_setter_compiler, 'disqus_title', 'set_disqus_title', ContextSetterNode)

def get_config(context):
    """
    return the formatted javascript for any disqus config variables
    """
    conf_vars = ['disqus_developer', 'disqus_identifier', 'disqus_url', 'disqus_title']
    
    output = []
    for item in conf_vars:
        if item in context:
            output.append('\tvar %s = %s;' % (item, context[item]))
    return '\n'.join(output)

def disqus_dev():
    """
    Return the HTML/js code to enable DISQUS comments on a local
    development server if settings.DEBUG is True.
    """
    if settings.DEBUG:
        return """<script type="text/javascript">
    var disqus_developer = 1;
    var disqus_url = 'http://%s/';
</script>""" % Site.objects.get_current().domain
    return ""

def disqus_num_replies(shortname=''):
    """
    Return the HTML/js code which transforms links that end with an
    #disqus_thread anchor into the threads comment count.
    """
    shortname = getattr(settings, 'DISQUS_WEBSITE_SHORTNAME', shortname)
    return """<script type="text/javascript">
    var disqus_shortname = '%(shortname)s';
    (function () {
        var s = document.createElement('script'); s.async = true;
        s.src = 'http://disqus.com/forums/%(shortname)s/count.js';
        (document.getElementsByTagName('HEAD')[0] || document.getElementsByTagName('BODY')[0]).appendChild(s);
    }());
</script>""" % dict(shortname=shortname)

def disqus_show_comments(shortname=''):
    """
    Return the HTML code to display DISQUS comments.
    """
    shortname = getattr(settings, 'DISQUS_WEBSITE_SHORTNAME', shortname)
    return """<div id="disqus_thread"></div>
<script type="text/javascript">
register.tag('set_disqus_developer', set_disqus_developer)
register.tag('set_disqus_identifier', set_disqus_identifier)
register.tag('set_disqus_url', set_disqus_url)
register.tag('set_disqus_title', set_disqus_title)
    /* <![CDATA[ */
    var disqus_shortname = '%(shortname)s';
    var disqus_domain = 'disqus.com';
    (function() {
        var dsq = document.createElement('script'); dsq.type = 'text/javascript';
        dsq.async = true;
        dsq.src = 'http://' + disqus_shortname + '.' + disqus_domain + '/embed.js';
        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
    })();
    /* ]]> */
</script>
<noscript>Please enable JavaScript to view the <a href="http://disqus.com/?ref_noscript=">comments powered by Disqus.</a></noscript>
<p><a href="http://disqus.com" class="dsq-brlink">blog comments powered by <span class="logo-disqus">Disqus</span></a></p>""" % dict(shortname=shortname)

register.simple_tag(disqus_dev)
register.simple_tag(disqus_num_replies)
register.simple_tag(disqus_show_comments)
