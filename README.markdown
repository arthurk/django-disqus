# django-disqus

Easily integrate [DISQUS](http://disqus.com) comments into your website.

* Templatetags to ease the integration
* Export comments from django.contrib.comments & django-threadedcomments to DISQUS
* Dump DISQUS JSON data into local file

## Installation

1. `easy_install django-disqus` or clone the git repo and run `python setup.py install`.
2. Add `disqus` to your `INSTALLED_APPS` setting.
3. Add `DISQUS_API_KEY` and `DISQUS_WEBSITE_SHORTNAME` to your settings. You
can [get your API key here](http://disqus.com/api/get_my_key/). The shortname 
of your site can be found in the right sidebar ("My Websites") on the 
[DISQUS homepage](http://disqus.com).

Example settings.py:
    
    INSTALLED_APPS = (
        ...
        'django.contrib.comments',
        'disqus',
    )

    DISQUS_API_KEY = 'FOOBARFOOBARFOOBARFOOBARFOOBARF'
    DISQUS_WEBSITE_SHORTNAME = 'foobar'

## Templatetags

Load templatetags with `{% load disqus_tags %}`.

### disqus\_dev

Disables url validation and sets the page URL associated with a comment thread 
to the current Site's domain if `DEBUG = True`.

This is neccesary to get comments working on a local development server.
    
    {% load disqus_tags %}
    <head>
      <meta http-equiv="Content-type" content="text/html; charset=utf-8">
      <title>fooar</title>
      {% disqus_dev %}
    </head>

### disqus\_show\_comments

Display comments and comment form.

    {% load disqus_tags %}
    {% disqus_show_comments %}

#### Options

* `title`: Defines the comment thread's title.
* `url`: Defines the page URL associated with a comment thread. Disqus uses this URL to uniquely create and identity a comment thread.
* `snippet`: Defines the page's content (article or blog post) to use as context.
* `shortname`: Use a different shortname than `settings.DISQUS_WEBSITE_SHORTNAME`


### disqus\_num\_replies

Replace all URLs that have the `#disqus_thread` anchor with their respective
comment count.

    {% load disqus_tags %}
    <a href="{{ object.get_absolute_url }}#disqus_thread">View Comments</a>
    {% disqus_num_replies %}

### disqus\_recent\_comments

Show recent comments.

    {% load disqus_tags %}
    {% disqus_recent_comments %}

#### Options

* `num_items`: Number of comments to show (default: 3)
* `avatar_size`: Size of the avatars (default: 32)
* `shortname`: Use a different shortname than `settings.DISQUS_WEBSITE_SHORTNAME`

## Management Commands

### disqus-export

Exports comments from django.contrib.comments to DISQUS.

When exporting comments, make sure you have the domain of your Site set. Also
the Model to which the comments are associated needs a `get_absolute_url()`
method which returns the absolute url to the page the comments should
appear on.

Threaded comments are not supported.

#### Options

* __-d/--dry-run__: Does not export any comments, but merely outputs the
comments which would have been exported
* __-v/--verbosity__: Output verbosity level; 0=minimal output, 1=normal output

### disqus-threadedcomments-export

Same as `disqus-export` but exports comments from `disqus-threadedcomments`.

### disqus-dumpdata

The `disqus-dumpdata` command dumps DISQUS comments into a local JSON file.

#### Options

* __--indent__: Specifies the indent level to use when pretty-printing output
