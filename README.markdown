# django-disqus

django-disqus helps you to easily integrate DISQUS comments into your website.

## Features

* Export django.contrib.comments to DISQUS
* Dump DISQUS into local JSON file
* Templatetags to ease the integration

## Requirements

 * Django 1.0.x

## Installation

1. `easy_install django-disqus` or checkout the git repo.
2. Add `disqus` to your `INSTALLED_APPS` setting.
3. Add `DISQUS_API_KEY` and `DISQUS_WEBSITE_SHORTNAME` to your settings.

Refer to the [http://wiki.disqus.net/API](DISQUS API) documentation if you
don't know how to get your API key.

You can find the shortname of your site on the DISQUS homepage in the right 
sidebar under "_My Websites_".

Example:

    # settings.py
    
    INSTALLED_APPS = (
        ...
        'django.contrib.comments',
        'disqus',
    )

    DISQUS_API_KEY = 'FOOBARFOOBARFOOBARFOOBARFOOBARF'
    DISQUS_WEBSITE_SHORTNAME = 'foobar'

## Management Commands

### disqus-export

The `disqus-export` command exports comments from django.contrib.comments to 
DISQUS.

When exporting comments, make sure you have the domain of your Site set. Also
the Model to which the comments are associated needs a `get_absolute_url()`
method which returns the absolute url to the page the comments should
appear on.

Threaded comments are not supported.

Options:

* __-d/--dry-run__: Does not export any comments, but merely outputs the
comments which would have been exported
* __-v/--verbosity__: Output verbosity level; 0=minimal output, 1=normal output

### disqus-dumpdata

The `disqus-dumpdata` command dumps DISQUS comments into a local JSON file.

Options:

* __--indent__: Specifies the indent level to use when pretty-printing output

### Templatetags

#### disqus\_dev

In order to get comments working on a local development server you need to 
include this templatetag in your website's `<head>`:

    <head>
      <meta http-equiv="Content-type" content="text/html; charset=utf-8">
      <title>fooar</title>
      {% disqus_dev %}
    </head>

If the `DEBUG` setting is set to `True` this sets the `disqus_developer` 
variable to `1` to disable url validation. It also sets `disqus_url` 
to the current Site's domain. Without this, it wouldn't be possible to display 
the comment form locally.

#### **disqus\_num\_replies**

Returns the JavaScript necessary to replace all permalinks which have the 
`#disqus_thread` anchor with the comment count for that url.

Example:

    <a href="{{ object.get_absolute_url }}#disqus_thread">View Comments</a>
    {% disqus_num_replies %}

#### **disqus\_show\_comments** 

Returns the JavaScript necessary to display the comment form and comments.

Example:

    {% disqus_show_comments %}
