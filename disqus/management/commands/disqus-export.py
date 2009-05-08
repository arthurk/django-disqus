from optparse import make_option

from django.conf import settings
from django.contrib import comments
from django.contrib.sites.models import Site, RequestSite
from django.core.management.base import NoArgsCommand
from django.utils import simplejson as json

from disqus import call

class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('-d', '--dry-run', action="store_true", dest="dry_run",
                    help='Does not export any comments, but merely outputs the comments which would have been exported.'),
        make_option('-v', '--verbosity', action='store', dest='verbosity', default='1',
                    type='choice', choices=['0', '1',],
                    help='Verbosity level; 0=minimal output, 1=normal output'),
    )
    
    help = 'Export django.contrib.comments to DISQUS'
    requires_model_validation = False
    
    def _get_comments_to_export(self):
        """
        Fetches the comments from the database which should be exported
        """
        return comments.get_model().objects.order_by('id').filter(is_public=True, 
                                                                  is_removed=False)
    
    def handle(self, **options):        
       	if Site._meta.installed: 
       	    current_site = Site.objects.get_current()
       	else: 
       	    current_site = RequestSite(request)
        
        verbosity = int(options.get('verbosity'))
        dry_run = int(options.get('verbosity'))            
        
        comments = self._get_comments_to_export()
        comments_count = comments.count()
        print "Exporting %d comment(s)" % comments_count
        if dry_run:
            print comments
            return
        
        if comments_count > 0:            
            # Get a list of all forums for an API key. Each API key can have 
            # multiple forums associated. This application only supports the one 
            # specified under DISQUS_WEBSITE_SHORTNAME
            forum_list = call('get_forum_list', 
                              {'user_api_key': settings.DISQUS_API_KEY})
            try:
                forum = [f for f in forum_list if f['shortname'] == settings.DISQUS_WEBSITE_SHORTNAME][0]
            except IndexError:
                raise CommandError("Could not find forum. " + 
                                   "Check your 'DISQUS_WEBSITE_SHORTNAME' setting.")
            
            # Get the API key for the forum. Each forum has an unique API key
            forum_api_key = call('get_forum_api_key', 
                                 {'user_api_key': settings.DISQUS_API_KEY, 
                                  'forum_id': forum['id']})
            
            for comment in comments:
                if verbosity >= 1:
                    print "Exporting comment '%s'" % comment
                
                # Construct the url under which the comment should appear
                content_obj = comment.content_object
                content_obj_url = 'http://%s%s' % (current_site.domain, 
                                                   content_obj.get_absolute_url())
                
                # Try to get the thread by the url, if it doesn't exist we
                # create a new thread with this url.
                thread = call('get_thread_by_url', {'forum_api_key': forum_api_key, 
                                                    'url': content_obj_url})
                if not thread:
                    # create a new thread
                    thread = call('thread_by_identifier', {
                        'forum_api_key': forum_api_key,
                        'identifier': content_obj,
                        'title': str(content_obj)}, True)['thread']
                    
                    # set the url of the thread
                    call('update_thread', {'forum_api_key': forum_api_key,
                                           'thread_id': thread['id'],
                                           'url': content_obj_url}, True)
                

                # name and email are optional in contrib.comments but required
                # in DISQUS. If they are not set there will be dummy values 
                # provided
                post_data = {'forum_api_key': forum_api_key,
                             'thread_id': thread['id'],
                             'message': comment.comment.encode("utf-8"),
                             'author_name': comment.user_name.encode("utf-8") or 'nobody',
                             'author_email': comment.user_email or 'nobody@example.org',
                             'author_url': comment.user_url,
                             'created_at':  comment.submit_date.strftime("%Y-%m-%dT%H:%M")}
                call('create_post', post_data, True)
