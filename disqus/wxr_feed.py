import datetime

from django import template
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed, add_domain
from django.utils import feedgenerator, tzinfo
from django.utils.encoding import iri_to_uri
try:
    from django.utils.encoding import force_text
except ImportError:
    # Django < 1.5
    from django.utils.encoding import force_unicode as force_text

USE_SINGLE_SIGNON = getattr(settings, "DISQUS_USE_SINGLE_SIGNON", False)

class WxrFeedType(feedgenerator.Rss201rev2Feed):
    def rss_attributes(self):
        return {
            'version': self._version,
            'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
            'xmlns:dsq': 'http://www.disqus.com/',
            'xmlns:dc': 'http://purl.org/dc/elements/1.1/',
            'xmlns:wp': 'http://wordpress.org/export/1.0/',
        }
    
    def format_date(self, date):
        return date.strftime('%Y-%m-%d %H:%M:%S')
    
    def add_item(self, title, link, description, author_email=None,
        author_name=None, author_link=None, pubdate=None, comments=None,
        unique_id=None, enclosure=None, categories=(), item_copyright=None,
        ttl=None, **kwargs):
        """
        Adds an item to the feed. All args are expected to be Python Unicode
        objects except pubdate, which is a datetime.datetime object, and
        enclosure, which is an instance of the Enclosure class.
        """
        to_unicode = lambda s: force_text(s, strings_only=True)
        if categories:
            categories = [to_unicode(c) for c in categories]
        if ttl is not None:
            # Force ints to unicode
            ttl = force_text(ttl)
        item = {
            'title': to_unicode(title),
            'link': iri_to_uri(link),
            'description': to_unicode(description),
            'author_email': to_unicode(author_email),
            'author_name': to_unicode(author_name),
            'author_link': iri_to_uri(author_link),
            'pubdate': pubdate,
            'comments': comments,
            'unique_id': to_unicode(unique_id),
            'enclosure': enclosure,
            'categories': categories or (),
            'item_copyright': to_unicode(item_copyright),
            'ttl': ttl,
        }
        item.update(kwargs)
        self.items.append(item)
    
    def add_root_elements(self, handler):
        pass
    
    def add_item_elements(self, handler, item):
        if item['comments'] is None:
            return
        handler.addQuickElement('title', item['title'])
        handler.addQuickElement('link', item['link'])
        handler.addQuickElement('content:encoded', item['description'])
        handler.addQuickElement('dsq:thread_identifier', item['unique_id'])
        handler.addQuickElement('wp:post_date_gmt',
            self.format_date(item['pubdate']).decode('utf-8'))
        handler.addQuickElement('wp:comment_status', item['comment_status'])
        self.write_comments(handler, item['comments'])
        
    def add_comment_elements(self, handler, comment):
        if USE_SINGLE_SIGNON:
            handler.startElement('dsq:remote', {})
            handler.addQuickElement('dsq:id', comment['user_id'])
            handler.addQuickElement('dsq:avatar', comment['avatar'])
            handler.endElement('dsq:remote')
        handler.addQuickElement('wp:comment_id', comment['id'])
        handler.addQuickElement('wp:comment_author', comment['user_name'])
        handler.addQuickElement('wp:comment_author_email', comment['user_email'])
        handler.addQuickElement('wp:comment_author_url', comment['user_url'])
        handler.addQuickElement('wp:comment_author_IP', comment['ip_address'])
        handler.addQuickElement('wp:comment_date_gmt',
            self.format_date(comment['submit_date']).decode('utf-8'))
        handler.addQuickElement('wp:comment_content', comment['comment'])
        handler.addQuickElement('wp:comment_approved', comment['is_approved'])
        if comment['parent'] is not None:
            handler.addQuickElement('wp:comment_parent', comment['parent'])
    
    def write_comments(self, handler, comments):
        for comment in comments:
            handler.startElement('wp:comment', {})
            self.add_comment_elements(handler, comment)
            handler.endElement('wp:comment')


class BaseWxrFeed(Feed):
    feed_type = WxrFeedType
    
    def get_feed(self, obj, request):
        current_site = Site.objects.get_current()
        
        link = self._Feed__get_dynamic_attr('link', obj)
        link = add_domain(current_site.domain, link)
        feed = self.feed_type(
            title = self._Feed__get_dynamic_attr('title', obj),
            link = link,
            description = self._Feed__get_dynamic_attr('description', obj),
        )
        
        title_tmp = None
        if self.title_template is not None:
            try:
                title_tmp = template.loader.get_template(self.title_template)
            except template.TemplateDoesNotExist:
                pass
        
        description_tmp = None
        if self.description_template is not None:
            try:
                description_tmp = template.loader.get_template(self.description_template)
            except template.TemplateDoesNotExist:
                pass
        
        for item in self._Feed__get_dynamic_attr('items', obj):
            if title_tmp is not None:
                title = title_tmp.render(
                    template.RequestContext(request, {
                        'obj': item, 'site': current_site
                    }))
            else:
                title = self._Feed__get_dynamic_attr('item_title', item)
            if description_tmp is not None:
                description = description_tmp.render(
                    template.RequestContext(request, {
                        'obj': item, 'site': current_site
                    }))
            else:
                description = self._Feed__get_dynamic_attr('item_description', item)
            link = add_domain(
                current_site.domain,
                self._Feed__get_dynamic_attr('item_link', item),
            )
            
            pubdate = self._Feed__get_dynamic_attr('item_pubdate', item)
            if pubdate and not hasattr(pubdate, 'tzinfo'):
                ltz = tzinfo.LocalTimezone(pubdate)
                pubdate = pubdate.replace(tzinfo=ltz)
            
            feed.add_item(
                title = title,
                link = link,
                description = description,
                unique_id = self._Feed__get_dynamic_attr('item_guid', item, link),
                pubdate = pubdate,
                comment_status = self._Feed__get_dynamic_attr('item_comment_status', item, 'open'),
                comments = self._get_comments(item)
            )
        return feed
    
    def _get_comments(self, item):
        cmts = self._Feed__get_dynamic_attr('item_comments', item)
        output = []
        for comment in cmts:
            output.append({
                'user_id': self._Feed__get_dynamic_attr('comment_user_id', comment),
                'avatar': self._Feed__get_dynamic_attr('comment_avatar', comment),
                'id': str(self._Feed__get_dynamic_attr('comment_id', comment)),
                'user_name': self._Feed__get_dynamic_attr('comment_user_name', comment),
                'user_email': self._Feed__get_dynamic_attr('comment_user_email', comment),
                'user_url': self._Feed__get_dynamic_attr('comment_user_url', comment),
                'ip_address': self._Feed__get_dynamic_attr('comment_ip_address', comment),
                'submit_date': self._Feed__get_dynamic_attr('comment_submit_date', comment),
                'comment': self._Feed__get_dynamic_attr('comment_comment', comment),
                'is_approved': str(self._Feed__get_dynamic_attr('comment_is_approved', comment)),
                'parent': str(self._Feed__get_dynamic_attr('comment_parent', comment)),
            })
        return output
        

class ContribCommentsWxrFeed(BaseWxrFeed):
    link = "/"
    
    def item_comments(self, item):
        from django.contrib.comments.models import Comment
        
        ctype = ContentType.objects.get_for_model(item)
        return Comment.objects.filter(content_type=ctype, object_pk=item.pk)
    
    def item_guid(self, item):
        ctype = ContentType.objects.get_for_model(item)
        return "%s_%s" % (ctype.name, item.pk)
    
    def comment_id(self, comment):
        return comment.pk
    
    def comment_user_id(self, comment):
        return force_text(comment.user_id)
    
    def comment_user_name(self, comment):
        return force_text(comment.user_name)
    
    def comment_user_email(self, comment):
        return force_text(comment.user_email)
    
    def comment_user_url(self, comment):
        return force_text(comment.user_url)
    
    def comment_ip_address(self, comment):
        return force_text(comment.ip_address)
    
    def comment_submit_date(self, comment):
        return comment.submit_date
    
    def comment_comment(self, comment):
        return comment.comment
    
    def comment_is_approved(self, comment):
        return int(comment.is_public)
    
    comment_parent = 0
