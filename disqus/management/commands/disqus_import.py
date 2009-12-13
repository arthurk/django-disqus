from datetime import datetime
from optparse import make_option
from urllib2 import URLError

from django.core.management.base import NoArgsCommand, CommandError

from disqus.api import DisqusClient
from disqus.models import Forum, Thread, Post, Author, AnonymousAuthor


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

    def import_threads(self, user_api_key, forum):
        "Import Threads from the Disqus API"
        client = DisqusClient()
        start = 0
        limit = 1000
        threads = []
        has_threads = True
        while has_threads:
            new_threads = client.get_thread_list(
                user_api_key=user_api_key,
                forum_id=forum.id,
                limit=limit, start=start)
            if not new_threads:
                has_threads = False
            else:
                threads.extend(new_threads)
                start += limit
        for thread in threads:
            date = datetime.strptime(thread['created_at'],
                        '%Y-%m-%dT%H:%M').strftime("%Y-%m-%d %H:%M")
            t = Thread(
                id = thread['id'],
                forum = forum,
                slug = thread['slug'],
                title = thread['title'],
                created_at = date,
                allow_comments = thread['allow_comments'],
                url = thread['url'],
                identifier = ' '.join(thread['identifier']))
            t.save()

    def import_posts(self, user_api_key, forum):
        "Import Posts from the Disqus API"
        client = DisqusClient()
        start = 0
        limit = 1000
        posts = []
        has_posts = True
        while has_posts:
            new_posts = client.get_forum_posts(
                user_api_key=user_api_key,
                forum_id=forum.id,
                limit=limit, start=start,
                exclude='spam,killed')
            if not new_posts:
                has_posts = False
            else:
                posts.extend(new_posts)
                start += limit
        for post in posts:
            try:
                thread = Thread.objects.get(id=post['thread']['id'])
            except Thread.DoesNotExist:
                continue
            date = datetime.strptime(post['created_at'],
                        '%Y-%m-%dT%H:%M').strftime("%Y-%m-%d %H:%M")

            if post['is_anonymous']:
                # anonymouse user
                anon_author = AnonymousAuthor(
                    url=post['anonymous_author']['url'],
                    email=post['anonymous_author']['email'],
                    email_hash=post['anonymous_author']['email_hash'],
                    name=post['anonymous_author']['name'])
                anon_author.save()
                author = None
            else:
                # registered user
                author = Author(
                    id=post['author']['id'],
                    url=post['author']['url'],
                    username=post['author']['username'],
                    email=post['author']['email'],
                    email_hash=post['author']['email_hash'],
                    has_avatar=post['author']['has_avatar'],
                    display_name=post['author']['display_name'])
                author.save()
                anon_author = None

            p = Post(id=post['id'],
                     forum = forum,
                     thread = thread,
                     created_at = date,
                     message = post['message'],
                     parent_post = post['parent_post'],
                     ip_address = post['ip_address'],
                     has_been_moderated = post['has_been_moderated'],
                     status = post['status'],
                     points = post['points'],
                     is_anonymous = post['is_anonymous'],
                     anonymous_author = anon_author,
                     author = author)
            p.save()

    def handle_noargs(self, **options):
        from django.conf import settings

        user_api_key = settings.DISQUS_API_KEY
        forum_shortname = settings.DISQUS_WEBSITE_SHORTNAME

        print 'Importing Forums'
        self.import_forums(user_api_key)
        forum = self.get_forum(forum_shortname)
        print 'Importing Threads for Forum "%s"' % forum
        self.import_threads(user_api_key, forum)
        threads = Thread.objects.all()
        print 'Importing Posts for Forum "%s"' % forum
        self.import_posts(user_api_key, forum)
