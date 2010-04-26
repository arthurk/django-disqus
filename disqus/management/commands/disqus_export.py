from optparse import make_option

from django.conf import settings
from django.contrib import comments
from django.contrib.sites.models import Site
from django.core.management.base import NoArgsCommand
from django.utils import simplejson as json

from disqus.api import DisqusClient


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('-d', '--dry-run', action="store_true", dest="dry_run",
                    help='Does not export any comments, but merely outputs' +
                         'the comments which would have been exported.'),
    )
    help = 'Export comments from contrib.comments to DISQUS'
    requires_model_validation = False

    def _get_comments_to_export(self):
        """Return comments which should be exported."""
        return comments.get_model().objects.order_by('id').filter(is_public=True,
                                                                  is_removed=False)

    def handle(self, **options):
        current_site = Site.objects.get_current()
        client = DisqusClient()
        verbosity = int(options.get('verbosity'))
        dry_run = bool(options.get('dry_run'))

        comments = self._get_comments_to_export()
        comments_count = comments.count()
        if verbosity >= 1:
            print "Exporting %d comment(s)" % comments_count

        # if this is a dry run, we output the comments and exit
        if dry_run:
            print comments
            return
        # if no comments were found we also exit
        if not comments_count:
            return

        # Get a list of all forums for an API key. Each API key can have 
        # multiple forums associated. This application only supports the one 
        # set in the DISQUS_WEBSITE_SHORTNAME variable
        forum_list = client.get_forum_list(user_api_key=settings.DISQUS_API_KEY)
        try:
            forum = [f for f in forum_list\
                     if f['shortname'] == settings.DISQUS_WEBSITE_SHORTNAME][0]
        except IndexError:
            raise CommandError("Could not find forum. " +
                               "Please check your " +
                               "'DISQUS_WEBSITE_SHORTNAME' setting.")

        # Get the forum API key
        forum_api_key = client.get_forum_api_key(
            user_api_key=settings.DISQUS_API_KEY,
            forum_id=forum['id'])

        for comment in comments:
            if verbosity >= 1:
                print "Exporting comment '%s'" % comment

            # Try to find a thread with the comments URL.
            url = 'http://%s%s' % (
                current_site.domain,
                comment.content_object.get_absolute_url())
            thread = client.get_thread_by_url(
                url=url,
                forum_api_key=forum_api_key)

            # if no thread with the URL could be found, we create a new one.
            # to do this, we first need to create the thread and then 
            # update the thread with a URL.
            if not thread:
                thread = client.thread_by_identifier(
                    forum_api_key=forum_api_key,
                    identifier=unicode(comment.content_object),
                    title=unicode(comment.content_object),
                )['thread']
                client.update_thread(
                    forum_api_key=forum_api_key,
                    thread_id=thread['id'],
                    url=url)

            # name and email are optional in contrib.comments but required
            # in DISQUS. If they are not set, dummy values will be used
            client.create_post(
                forum_api_key=forum_api_key,
                thread_id=thread['id'],
                message=comment.comment.encode('utf-8'),
                author_name=comment.userinfo.get('name',
                                                 'nobody').encode('utf-8'),
                author_email=comment.userinfo.get('email',
                                                  'nobody@example.org'),
                author_url=comment.userinfo.get('url', ''),
                created_at=comment.submit_date.strftime('%Y-%m-%dT%H:%M'))
