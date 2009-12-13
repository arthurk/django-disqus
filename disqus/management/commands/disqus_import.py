from datetime import datetime
from optparse import make_option
from urllib2 import URLError

from django.core.management.base import NoArgsCommand, CommandError

from disqus.api import DisqusClient
from disqus.models import Forum, Thread, Post


class Command(NoArgsCommand):
    help = 'Import DISQUS data into the local database'

    def import_forums(self, user_api_key):
        "Import forums from the Disqus API"
        client = DisqusClient()
        try:
            forums = client.get_forum_list(user_api_key=user_api_key)
        except URLError, e:
            raise CommandError('Could not get forums. Check your ' \
                               '"DISQUS_API_KEY" setting.')
        for forum in forums:
            f = Forum(id = forum['id'],
                      shortname = forum['shortname'],
                      name = forum['name'])
            f.save()

    def get_forum(self, shortname):
        try:
            return Forum.objects.get(shortname=shortname)
        except Forum.DoesNotExist:
            raise CommandError('Could not find forum with shortname "%s". ' \
                               'Check your "DISQUS_WEBSITE_SHORTNAME" ' \
                               'setting.' % shortname)

    def import_threads(self):
        "Import Threads from the Disqus API"
        pass

    def import_posts(self):
        "Import Posts from the Disqus API"
        pass

    def handle_noargs(self, **options):
        from django.conf import settings

        print 'Importing Forums'
        self.import_forums(user_api_key=settings.DISQUS_API_KEY)
        forum = self.get_forum(settings.DISQUS_WEBSITE_SHORTNAME)
