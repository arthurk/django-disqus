from optparse import make_option

from django.core.management.base import NoArgsCommand, CommandError
from django.core import serializers
from django.utils import simplejson as json

from disqus import call

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--indent', default=None, dest='indent', type='int',
            help='Specifies the indent level to use when pretty-printing output'),
    )
    
    help = 'Output DISQUS data in JSON format'
    requires_model_validation = False

    def handle(self, *app_labels, **options):
        from django.conf import settings
        
        data = {}
        indent = options.get('indent', None)
        
        # Get a list of all forums for an API key. Each API key can have 
        # multiple forums associated. This application only supports the one 
        # specified under DISQUS_WEBSITE_SHORTNAME
        forum_list = call('get_forum_list', 
                          {'user_api_key': settings.DISQUS_API_KEY})
        try:
            data['forum'] = [f for f in forum_list if f['shortname'] == settings.DISQUS_WEBSITE_SHORTNAME][0]
        except IndexError:
            raise CommandError("Could not find forum. " + 
                               "Check your 'DISQUS_WEBSITE_SHORTNAME' setting.")
 
        # Get the API key for the forum. Each forum has an unique API key
        forum_api_key = call('get_forum_api_key', 
                             {'user_api_key': settings.DISQUS_API_KEY, 
                              'forum_id': data['forum']['id']})
        
        # Get the threads for a forum
        data['forum']['threads'] = call('get_thread_list', 
                                        {'forum_api_key': forum_api_key})
        
        # Get the posts for each thread
        for thread in data['forum']['threads']:
            thread['posts'] = call('get_thread_posts', 
                                   {'forum_api_key': forum_api_key,
                                    'thread_id': thread['id']})
        
        # Output the data
        print json.dumps(data, indent=indent)
