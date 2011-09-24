from optparse import make_option
import os.path
import sys
import urllib2

from django.conf import settings
from django.contrib import comments
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import NoArgsCommand
from django.utils import simplejson as json

from disqus.api import DisqusClient


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('-d', '--dry-run', action="store_true", dest="dry_run",
                    help='Does not export any comments, but merely outputs' +
                         'the comments which would have been exported.'),
        make_option('-s', '--state-file', action="store", dest="state_file",
                    help="Saves the state of the export in the given file " +
                         "and auto-resumes from this file if possible."),
        make_option('-j', '--jump-store', action="store_true", dest="jump_store",
                    help="If --state-file is specified then skip the first "
                    "comment in the state file. Used to get around corrupt comments."),
        make_option('-c', '--continue-on-error', action="store_true", dest="continue_on_error",
                    help="If an error is encountered print a warning and continue. " +
                         "Default behaviour is to quit."),
    )
    help = 'Export comments from contrib.comments to DISQUS'
    requires_model_validation = False

    def _get_comments_to_export(self, last_export_id=None):
        """Return comments which should be exported."""
        qs = comments.get_model().objects.order_by('pk')\
                .filter(is_public=True, is_removed=False)
        if last_export_id is not None:
            print "Resuming after comment %s" % str(last_export_id)
            qs = qs.filter(id__gt=last_export_id)
        return qs

    def _get_last_state(self, state_file):
        """Checks the given path for the last exported comment's id"""
        state = None
        fp = open(state_file)
        try:
            state = int(fp.read())
            print "Found previous state: %d" % (state,)
        finally:
            fp.close()
        return state

    def _save_state(self, state_file, last_pk):
        """Saves the last_pk into the given state_file"""
        fp = open(state_file, 'w+')
        try:
            fp.write(str(last_pk))
        finally:
            fp.close()

    def handle(self, **options):
        current_site = Site.objects.get_current()
        client = DisqusClient()
        verbosity = int(options.get('verbosity'))
        dry_run = bool(options.get('dry_run'))
        state_file = options.get('state_file')
        jump_store = bool(options.get('jump_store'))
        continue_on_error = bool(options.get('continue_on_error'))
        last_exported_id = None

        if state_file is not None and os.path.exists(state_file):
            last_exported_id = self._get_last_state(state_file)
            if jump_store:
                last_exported_id += 1

        exp_comments = self._get_comments_to_export(last_exported_id)
        comments_count = exp_comments.count()
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

        for i, comment in enumerate(exp_comments):
            if verbosity >= 1:
                print "Exporting comment %s/%s (%s%%)" % \
                   (i+1, comments_count, round((float(i)/comments_count)*100, 2)),

            comment_str = None
            try:
                # Try to find a thread with the comments URL.
                url_path = comment.content_object.get_absolute_url()
                comment_str = str(comment).replace('\n', '').replace('\r', '')
            except (AttributeError, ObjectDoesNotExist), e:
                print
                print 'ERROR: %s' % e
                if comment_str is not None:
                    print '  Comment contents: "%s"' % (str(comment)[:30],)
                if comment.content_object is not None:
                    model = comment.content_object.__class__
                else:
                    model = comment.content_object
                print '  Comment pk: %s. Content object: %s (model: %s - pk: %s)' % \
                    (comment.pk, comment.content_object, model, comment.object_pk,)
                if continue_on_error:
                    continue
                else:
                    sys.exit(1)

            if verbosity >= 1:
                print ": '%s'" % (comment_str,)

            url = 'http://%s%s' % (
                current_site.domain,
                url_path)
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
            try:
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
            except urllib2.HTTPError, e:
                if verbosity == 0:
                  sys.exit(1)
                print e
                print dir(e)
                print 'HTTP: args: ', e.args
                print 'HTTP: code:', e.code
                print 'HTTP: errno:', e.errno
                print 'HTTP: geturl:', e.geturl()
                print 'HTTP: headers:', e.headers
                print 'HTTP: msg:', e.msg
                print 'HTTP: strerror:', e.strerror
                print 'HTTP: url:', e.url
                sys.exit(1)

            if state_file is not None:
                self._save_state(state_file, comment.pk)
