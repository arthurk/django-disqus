from optparse import make_option
from django.core.management.base import NoArgsCommand, CommandError
from disqus.api import DisqusClient
from disqus.models import Forum

class Command(NoArgsCommand):
    help = 'Import DISQUS data into local database'

    def handle_noargs(self, **options):
        from django.conf import settings

        client = DisqusClient()
        forums = client.get_forum_list(user_api_key=settings.DISQUS_API_KEY)
        try:
            forum = [f for f in forums if f['shortname'] == settings.DISQUS_WEBSITE_SHORTNAME][0]
        except IndexError:
            raise CommandError("Could not find forum with shortname '%s'. " \
                               "Check your 'DISQUS_WEBSITE_SHORTNAME' " \
                               "setting" % setting.DISQUS_WEBSITE_SHORTNAME)
        forum_obj = Forum.objects.get_or_create(id=forum['id'], defaults=dict(
            shortname=forum['shortname'],
            name=forum['name']
        ))
