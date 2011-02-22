=========================
Exporting Comments as WXR
=========================

The WXR feed is an XML document that contains the item upon which people commented as well as the comments. The Disqus WXR feed is a superset of the the typical RSS feed, and therefore works very much like a typical Django syndication feed.

Create a ContribCommentsWxrFeed Subclass
========================================

``ContribCommentsWxrFeed`` exports ``django.contrib.comments`` for a set of items. This example exports comments to entries of a fictional blogging app.

.. code-block:: python

	from disqus.wxr_feed import ContribCommentsWxrFeed
	from coolblog.models import Entry

	class EntryWxrFeed(ContribCommentsWxrFeed):
	    link = "/"

	    def items(self):
	        return Entry.objects.all()

	    def item_pubdate(self, item):
	        return item.pub_date

	    def item_description(self, item):
	        return item.content


All WxrFeed Attributes
======================

For a full explanation of how you can define these attributes, see Django's `syndication documentation <http://docs.djangoproject.com/en/dev/ref/contrib/syndication/>`_.

**title_template** or **item_title**
	If ``title_template`` exists, the template is rendered with ``obj`` and ``site`` in the context, otherwise ``item_title`` is used.
	
	This attribute becomes the ``<title>`` element.

**description_template** or **item_description**
	If ``description_template`` exists, the template is rendered with ``obj`` and ``site`` in the context, otherwise ``item_description`` is used.
	
	This attribute becomes the ``<content:encoded>`` element.

**item_pubdate**
	When the item was published.
	
	The attribute becomes the ``<wp:post_date_gmt>`` element.

**item_guid**
	A unique identifier for this item. By default it is the item's content type name and the item's id, separated by an underscore (_). This allows for exporting comments on several different things without id collisions.
	
	This attribute becomes the ``<dsq:thread_identifier>`` element.

**item_comment_status**
	Can people comment on this item? One of either ``open`` or ``closed``\ . 
	
	This attribute becomes the ``<wp:comment_status>`` element.

**item_comments**
	Return a list of comments for the given item. All comment attributes are mapped based on the attributes below.

**comment_id**
	The unique identifier for this comment.
	
	This attribute becomes the ``<wp:comment_id>`` element.

**comment_user_id**
	The unique identifier for the commenting user.
	
	This attribute becomes the ``<dsq:id>`` element.

**comment_avatar**
	The url to the commenting user's avatar
	
	This attribute becomes the ``<dsq:avatar>`` element.

**comment_user_name**
	The name of the commenting user.
	
	This attribute becomes the ``<wp:comment_author>`` element.

**comment_user_email**
	The email of the commenting user.
	
	This attribute becomes the ``<wp:comment_author_email>`` element.

**comment_user_url**
	The commenting user's URL.
	
	This attribute becomes the ``<wp:comment_author_url>`` element.

**comment_ip_address**
	The commenting user's IP address.
	
	This attribute becomes the ``<wp:comment_author_IP>`` element.

**comment_submit_date**
	The date and time when the comment was submitted.
	
	This attribute becomes the ``<wp:comment_date_gmt>`` element.

**comment_comment**
	The text of the content
	
	This attribute becomes the ``<wp:comment_content>`` element.

**comment_is_approved**
	The site moderators have approved this comment for public display. ``1`` for yes, and ``0`` for no.
	
	This attribute becomes the ``<wp:comment_approved>`` element.

**comment_parent**
	The id of the comment in which this comment is responding.
	
	This attribute becomes the ``<wp:comment_parent>`` element.