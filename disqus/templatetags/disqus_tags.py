from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.functional import curry
from django.utils.encoding import force_unicode

register = template.Library()

class ContextSetterNode(template.Node):
    def __init__(self, var_name, var_value):
        self.var_name = var_name
        self.var_value = var_value
    
    def _get_value(self, value, context):
        """
        Attempts to resolve the value as a variable. Failing that, it returns
        its actual value
        """
        try:
            var_value = template.Variable(value).resolve(context)
        except template.VariableDoesNotExist:
            var_value = self.var_value.var
        return var_value
    
    def render(self, context):
        if isinstance(self.var_value, (list, tuple)):
            var_value = ''.join([force_unicode(self._get_value(x, context)) for x in self.var_value])
        else:
            var_value = self._get_value(self.var_value, context)
        context[self.var_name] = var_value
        return ''

def generic_setter_compiler(var_name, name, node_class, parser, token):
    """
    Returns a ContextSetterNode.
    
    For calls like {% set_this_value "My Value" %}
    """
    bits = token.split_contents()
    if(len(bits) < 2):
        message = "%s takes at least one argument" % name
        raise template.TemplateSyntaxError(message)
    return node_class(var_name, bits[1:])

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
            output.append('\tvar %s = "%s";' % (item, context[item]))
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

def disqus_num_replies(context, shortname=''):
    """
    Return the HTML/js code which transforms links that end with an
    #disqus_thread anchor into the threads comment count.
    """
    shortname = getattr(settings, 'DISQUS_WEBSITE_SHORTNAME', shortname)
    
    return {
        'shortname': shortname,
        'config': get_config(context),
    }

def disqus_show_comments(context, shortname=''):
    """
    Return the HTML code to display DISQUS comments.
    """
    shortname = getattr(settings, 'DISQUS_WEBSITE_SHORTNAME', shortname)
    return {
        'shortname': shortname,
        'config': get_config(context),
    }

register.tag('set_disqus_developer', set_disqus_developer)
register.tag('set_disqus_identifier', set_disqus_identifier)
register.tag('set_disqus_url', set_disqus_url)
register.tag('set_disqus_title', set_disqus_title)
register.simple_tag(disqus_dev)
register.inclusion_tag('disqus/num_replies.html', takes_context=True)(disqus_num_replies)
register.inclusion_tag('disqus/show_comments.html', takes_context=True)(disqus_show_comments)
