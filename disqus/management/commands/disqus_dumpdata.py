from __future__ import print_function

import json
from optparse import make_option

from django.core.management.base import NoArgsCommand, CommandError

from disqus.api import DisqusClient


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option('--indent', default=None, dest='indent', type='int',
            help='Specifies the indent level to use when pretty-printing output'),
        make_option('--filter', default='', dest='filter', type='str',
            help='Type of entries that should be returned'),
        make_option('--exclude', default='', dest='exclude', type='str',
            help='Type of entries that should be excluded from the response'),
    )
    help = 'Output DISQUS data in JSON format'
    requires_model_validation = False

    def handle(self, **options):
        from django.conf import settings

        client = DisqusClient()
        indent = options.get('indent')
        filter_ = options.get('filter')
        exclude = options.get('exclude')

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
        posts = []
        has_new_posts = True
        start = 0
        step = 100
        while has_new_posts:
            new_posts = client.get_forum_posts(
                user_api_key=settings.DISQUS_API_KEY,
                forum_id=forum['id'],
                start=start,
                limit=start+step,
                filter=filter_,
                exclude=exclude)
            if not new_posts:
                has_new_posts = False
            else:
                start += step
                posts.append(new_posts)
        print(json.dumps(posts, indent=indent))
