from datetime import datetime

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from disqus.api import DisqusClient


class Forum(models.Model):
    id = models.CharField(primary_key=True, max_length=15,
            help_text=_('A unique alphanumeric string identifying this ' \
                        'Forum object.'))
    shortname = models.CharField(max_length=200,
                    help_text=_('The unique string used in disqus.com URLs ' \
                                'relating to this forum.'))
    name = models.CharField(max_length=200,
            help_text=_('A string for displaying the forum\'s full title.'))

    class Meta:
        verbose_name = _('forum')
        verbose_name_plural = _('forums')

    def __unicode__(self):
        return self.name

    @staticmethod
    def import_from_api():
        client = DisqusClient()
        forums = client.get_forum_list(user_api_key=settings.DISQUS_API_KEY)
        for forum in forums:
            f = Forum(
                id = forum['id'],
                shortname = forum['shortname'],
                name = forum['name'])
            f.save()


class Thread(models.Model):
    id = models.CharField(primary_key=True, max_length=15,
            help_text=_('A unique alphanumeric string identifying this ' \
                        'Thread object.'))
    forum = models.ForeignKey('Forum',
                help_text=_('The id for the forum this thread belongs to.'))
    slug = models.CharField(max_length=200,
            help_text=_('The per-forum-unique string used for identifying ' \
                        'this thread in disqus.com URLs relating to this ' \
                        'thread. Composed of underscore-separated ' \
                        'alphanumeric strings.'))
    title = models.CharField(max_length=200,
                help_text=_('The title of the thread.'))
    created_at = models.DateTimeField(
                    help_text=_('The UTC date this thread was created.'))
    allow_comments = models.BooleanField(
                        help_text=_('Whether this thread is open to ' \
                                    'new comments.'))
    url = models.CharField(blank=True, null=True, max_length=200,
            help_text=_('The URL this thread is on, if known.'))
    identifier = models.CharField(blank=True, null=True, max_length=200,
                    help_text=_('The user-provided identifier for this ' \
                                'thread, as in thread_by_identifier above ' \
                                '(if available)'))
    class Meta:
        verbose_name = _('thread')
        verbose_name_plural = _('threads')

    def __unicode__(self):
        return self.title

    @staticmethod
    def import_from_api(forum):
        client = DisqusClient()
        threads = client.get_thread_list(user_api_key=settings.DISQUS_API_KEY,
                                         forum_id=forum.id,
                                         limit=65000, start=0)
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
                identifier = thread['identifier'][0])
            t.save()


class Post(models.Model):
    id = models.CharField(primary_key=True, max_length=15,
            help_text=_('A unique alphanumeric string identifying this '\
                        'Post object.'))
    forum = models.ForeignKey('Forum',
                help_text=_('The id for the forum this post belongs to.'))
    thread = models.ForeignKey('Thread',
                help_text=_('The id for the thread this post belongs to.'))
    created_at = models.DateTimeField(
                    help_text=_('The UTC date this post was created.'))
    message = models.TextField(help_text=_('The contents of the post.'))
    parent_post = models.ForeignKey('self', blank=True, null=True,
                    help_text=_('The id of the parent post, if any'))
    shown = models.BooleanField(
                help_text=_('Whether the post is currently visible or not.'))
    is_anonymous = models.BooleanField(
                    help_text=_('Whether the comment was left anonymously, ' \
                                'as opposed to a registered Disqus account.'))
    anonymous_author = models.ForeignKey('AnonymousAuthor', blank=True,
                        null=True,
                        help_text=_('Present only when is_anonymous is true'))
    author = models.ForeignKey('Author', blank=True, null=True,
                help_text=_('Present only when is_anonymous is false'))
    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')

    def __unicode__(self):
        return "%s object: '%s'" % (self.__class__.__name__, self.id)


class AnonymousAuthor(models.Model):
    name = models.CharField(max_length=200,
            help_text=_('The display name of the commenter'))
    url = models.CharField(blank=True, null=True, max_length=200,
            help_text=_('Their optionally provided homepage'))
    email_hash = models.CharField(max_length=32,
                    help_text=_('md5 of the author\'s email address'))

    class Meta:
        verbose_name = _('anonymous author')
        verbose_name_plural = _('anonymous authors')

    def __unicode__(self):
        return self.name


class Author(models.Model):
    id = models.CharField(primary_key=True, max_length=15,
            help_text=_('The unique id of the commenter\'s Disqus account'))
    username = models.CharField(max_length=200,
                help_text=_('The author\'s username'))
    display_name = models.CharField(blank=True, null=True, max_length=200,
                    help_text=_('The author\'s full name, if provided'))
    url = models.CharField(blank=True, null=True, max_length=200,
            help_text=_('Their optionally provided homepage'))
    email_hash = models.CharField(max_length=32,
                    help_text=_('md5 of the author\'s email address'))
    has_avatar = models.BooleanField(
                    help_text=_('Whether the user has an avatar ' \
                                'on disqus.com'))

    class Meta:
        verbose_name = _('author')
        verbose_name_plural = _('authors')

    def __unicode__(self):
        return self.username
