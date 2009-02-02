from optparse import make_option
import urllib
import urllib2

from django.core.management.base import NoArgsCommand, CommandError
from django.core import serializers
from django.utils import simplejson as json


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--indent', default=None, dest='indent', type='int',
            help='Specifies the indent level to use when pretty-printing output'),
    )
    help = 'Output DISQUS data in JSON format.'
    requires_model_validation = False

    def _call(self, method, data, post=False):
        """
        Calls `method` from disqus API with data either in POST or GET mode and 
        returns deserialized JSON response.
        """
        url = "%s%s" % ('http://disqus.com/api/', method)
        if post:
            # POST request
            url += "/"
            data = urllib.urlencode(data)
        else:
            # GET request
            url += "?%s" % urllib.urlencode(data)
            data = ''
        res = json.load(urllib2.urlopen(url, data))
        if not res['succeeded']:
            raise CommandError("'%s' failed: %s" % (method, res['code']))
        return res['message']

    def handle(self, *app_labels, **options):
        from django.conf import settings
        
        indent = options.get('indent', None)
        data = {}
        
        # Forum
        forum_list = self._call('get_forum_list', 
                                {'user_api_key': settings.DISQUS_API_KEY})
        forum = None
        for forum_item in forum_list:
            if forum_item['shortname'] == settings.DISQUS_WEBSITE_SHORTNAME:
                forum = forum_item
        
        if not forum:
            raise CommandError("Could not find specified forum. " + 
                               "Check your 'DISQUS_WEBSITE_SHORTNAME' setting.")
        
        # API-Key for forums
        forum_api_key = self._call('get_forum_api_key', 
                                    {'user_api_key': settings.DISQUS_API_KEY, 
                                     'forum_id': forum['id']})
        data['forum'] = forum

        # Threads
        thread_list = self._call('get_thread_list', 
                                 {'forum_api_key': forum_api_key})
        
        data['forum']['threads'] = thread_list
        
        # Posts
        for thread_item in thread_list:
            thread_posts = self._call('get_thread_posts', 
                                          {'forum_api_key': forum_api_key,
                                           'thread_id': thread_item['id']})
            thread_item['posts'] = thread_posts
        
        print json.dumps(data, indent=indent)
