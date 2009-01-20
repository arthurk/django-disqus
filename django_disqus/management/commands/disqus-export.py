from optparse import make_option
import urllib
import urllib2

import simplejson as json

from django.core.management.base import NoArgsCommand


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
    
    def _call(self, method, data, post=False):
        """
        Calls `method` from disqus API with data either in POST or GET mode and 
        returns deserialized JSON response.
        
        TODO: Check if response was successful
              {'message': None, 'code': 'ok', 'succeeded': True}
            
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
        return json.loads(urllib2.urlopen(url, data).read())
    
    def handle(self, **options):
        from django.conf import settings
        from django.contrib.sites.models import Site
        from django.contrib import comments
        
        current_site = Site.objects.get_current()
        verbosity = int(options.get('verbosity'))
        
        comments = comments.get_model().objects.order_by('id').filter(is_public__exact=True, 
                                                                      is_removed__exact=False)
        comments_count = comments.count()
        print "Exporting %d comment(s)" % comments_count
        
        if comments_count > 0:
            forums = self._call('get_forum_list', {'user_api_key': settings.DISQUS_API_KEY})
            
            for forum in forums['message']:
                if forum['shortname'] == settings.DISQUS_WEBSITE_SHORTNAME:
                    forum_id = forum['id']

            forum_api_key = self._call('get_forum_api_key', 
                                       {'user_api_key': settings.DISQUS_API_KEY, 
                                        'forum_id': forum_id})['message']
            
            for comment in comments:
                if verbosity >= 1:
                    print "Exporting comment '%s'" % comment
                
                content_obj = comment.content_object
                content_obj_url = 'http://%s%s' % (current_site.domain, 
                                                   content_obj.get_absolute_url())
                #print comment.get_content_object_url()
                
                thread = self._call('get_thread_by_url', {'forum_api_key': forum_api_key, 
                                                          'url': content_obj_url})['message']

                print content_obj.get_allow_comments()
                return

                # if no thread was found for the content object's url, create 
                # a new one
                if not thread:
                    # TODO: figure out better identifier for thread
                    thread = self._call('thread_by_identifier', {
                                            'forum_api_key': forum_api_key,
                                            'identifier': content_obj,
                                            'title': str(content_obj)}, True)['message']['thread']
                    
                    # set the url of the thread
                    # TODO: getattr content.obj slug, allow_comments etc.
                    self._call('update_thread', {'forum_api_key': forum_api_key,
                                                 'thread_id': thread['id'],
                                                 'url': content_obj_url}, True)
                
                # export comment
                post_data = {'forum_api_key': forum_api_key,
                             'thread_id': thread['id'],
                             'message': comment.comment.encode("utf-8"),
                             'author_name': comment.user_name.encode("utf-8"),
                             'author_email': comment.user_email,
                             'author_url': comment.user_url,
                             'ip_address': comment.ip_address,
                             'created_at':  comment.submit_date.strftime("%Y-%m-%dT%H:%M")}
                self._call('create_post', post_data, True)
