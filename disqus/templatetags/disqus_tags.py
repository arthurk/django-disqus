import base64
import hashlib
import hmac
import simplejson
import time

from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils.functional import curry
from django.utils.encoding import force_unicode

register = template.Library()

# Set the disqus_developer variable to 0/1. Default is 0
@register.simple_tag(takes_context=True)
def set_disqus_developer(context, disqus_developer):
    context['disqus_developer'] = disqus_developer
    return ""

# Set the disqus_identifier variable to some unique value. Defaults to page's URL
@register.simple_tag(takes_context=True)
def set_disqus_identifier(context, *args):
    context['disqus_identifier'] = "".join(args)
    return ""

# Set the disqus_url variable to some value. Defaults to page's location
@register.simple_tag(takes_context=True)
def set_disqus_url(context, *args):
    context['disqus_url'] = "".join(args)
    return ""

# Set the disqus_title variable to some value. Defaults to page's title or URL
@register.simple_tag(takes_context=True)
def set_disqus_title(context, disqus_title):
    context['disqus_title'] = disqus_title
    return ""

# Set the disqus_category_id variable to some value. No default. See
# http://help.disqus.com/customer/portal/articles/472098-javascript-configuration-variables#disqus_category_id
@register.simple_tag(takes_context=True)
def set_disqus_category_id(context, disqus_category_id):
    context['disqus_category_id'] = disqus_category_id
    return ""

def get_config(context):
    """
    return the formatted javascript for any disqus config variables
    """
    conf_vars = ['disqus_developer', 'disqus_identifier', 'disqus_url',
        'disqus_title', 'disqus_category_id']
    
    output = []
    for item in conf_vars:
        if item in context:
            output.append('\tvar %s = "%s";' % (item, context[item]))
    return '\n'.join(output)

@register.simple_tag(takes_context=True)
def disqus_dev(context):
    """
    Return the HTML/js code to enable DISQUS comments on a local
    development server if settings.DEBUG is True.
    """
    if settings.DEBUG:
        return """<script type="text/javascript">
    var disqus_developer = 1;
    var disqus_url = '//%s%s';
</script>""" % (Site.objects.get_current().domain, context['request'].path)
    return ""

@register.inclusion_tag('disqus/sso.html', takes_context=True)
def disqus_sso(context, shortname='', login_url=None, logout_url=None, button_url=None, login_width=None, login_height=None):
    """
    Return the HTML/js code to enable DISQUS SSO - so logged in users on
    your site can be logged in to disqus seamlessly.
    """
    # we have to make it str rather than unicode or the HMAC blows up
    DISQUS_SECRET_KEY = str(getattr(settings, 'DISQUS_SECRET_KEY', None))
    if DISQUS_SECRET_KEY is None:
        return "<p>You need to set DISQUS_SECRET_KEY before you can use SSO</p>"
    DISQUS_PUBLIC_KEY = getattr(settings, 'DISQUS_PUBLIC_KEY', None)
    if DISQUS_PUBLIC_KEY is None:
        return "<p>You need to set DISQUS_PUBLIC_KEY before you can use SSO</p>"
    
    shortname = getattr(settings, 'DISQUS_WEBSITE_SHORTNAME', shortname)
    login_url = login_url if login_url else getattr(settings, 'LOGIN_URL', None)
    logout_url = logout_url if logout_url else getattr(settings, 'LOGOUT_URL', None)
    button_url = button_url if button_url else getattr(settings, 'DISQUS_LOGIN_BUTTON', None)
    login_width = login_width if login_width else getattr(settings, 'DISQUS_LOGIN_WINDOW_WIDTH', None)
    login_height = login_height if login_height else getattr(settings, 'DISQUS_LOGIN_WINDOW_HEIGHT', None)
    
    user = context['user']
    
    if user.is_anonymous():
        # use empty JSON object as per disqus SSO guide
        data = simplejson.dumps({})
    else:
        # create a JSON packet of our data attributes
        data = simplejson.dumps({
            'id': user.id,
            'username': user.username,
            'email': user.email,
        })
    # encode the data to base64
    message = base64.b64encode(data)
    # generate a timestamp for signing the message
    timestamp = int(time.time())
    # generate our hmac signature
    sig = hmac.HMAC(DISQUS_SECRET_KEY, '%s %s' % (message, timestamp), hashlib.sha1).hexdigest()
    
    return {
        'shortname': shortname,
        'config': get_config(context),
        'message': message,
        'hmac': sig,
        'timestamp': timestamp,
        'public_api_key': DISQUS_PUBLIC_KEY,
        'button_url': button_url,
        'login_url': login_url,
        'logout_url': logout_url,
        'login_width': login_width,
        'login_height': login_height,
    }

@register.inclusion_tag('disqus/num_replies.html', takes_context=True)
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

@register.inclusion_tag('disqus/recent_comments.html', takes_context=True)
def disqus_recent_comments(context, shortname='', num_items=5, excerpt_length=200, hide_avatars=0, avatar_size=32):
    """
    Return the HTML/js code which shows recent comments.

    """
    shortname = getattr(settings, 'DISQUS_WEBSITE_SHORTNAME', shortname)
    
    return {
        'shortname': shortname,
        'num_items': num_items,
        'hide_avatars': hide_avatars,
        'avatar_size': avatar_size,
        'excerpt_length': excerpt_length,
        'config': get_config(context),
    }

@register.inclusion_tag('disqus/show_comments.html', takes_context=True)
def disqus_show_comments(context, shortname=''):
    """
    Return the HTML code to display DISQUS comments.
    """
    shortname = getattr(settings, 'DISQUS_WEBSITE_SHORTNAME', shortname)
    return {
        'shortname': shortname,
        'config': get_config(context),
    }
