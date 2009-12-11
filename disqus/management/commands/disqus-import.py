from optparse import make_option
from django.core.management.base import NoArgsCommand, CommandError
from disqus.api import DisqusClient
from disqus.models import Forum

class Command(NoArgsCommand):
    help = 'Import DISQUS data into the local database'

    def handle_noargs(self, **options):
        from django.conf import settings

        Forum.import_from_api()
        try:
            forum = Forum.objects.get(shortname=settings.DISQUS_WEBSITE_SHORTNAME)
        except Forum.DoesNotExist:
            raise CommandError("Could not find forum with shortname '%s'. " \
                               "Check your 'DISQUS_WEBSITE_SHORTNAME' " \
                               "setting" % setting.DISQUS_WEBSITE_SHORTNAME)
