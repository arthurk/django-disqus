# django-disqus

**WORK IN PROGRESS!**

## Features

* Export comments from django.contrib.comments to DISQUS.
* Dump data from DISQUS in local JSON file.
* Templatetags

## Requirements

 * Django 1.0

## Installation

1. Add 'disqus' to your INSTALLED\_APPS.
2. Add "DISQUS\_API\_KEY" and "DISQUS\_WEBSITE\_SHORTNAME" to your settings file. You can [http://disqus.com/api/get_my_key/][get your API key here].

## Usage

### Exporting comments

To export comments to disqus:

    python manage.py disqus-export

### Dumping data

To dump the data from disqus:
    
    python manage.py disqus-dumpdata

You can pass the --indent option to specify the indentation of the output:
    
    python manage.py disqus-dumpdata --indent=4

### Templatetags

#### disqus\_dev

In order to get comments working on a local development server you need to 
include the templatetag in your website's `<head>` tag:

    <head>
      <meta http-equiv="Content-type" content="text/html; charset=utf-8">
      <title>fooar</title>
      {% load disqus_tags %}
      {% disqus_dev %}
    </head>

It sets `disqus_developer` to `1` and `disqus_url` to the current site's 
url if the `DEBUG` setting of your project is set to `True`.

#### **disqus\_num\_replies**

Returns the JavaScript necessary to show the current comment count.
The JavaScript will replace all permalinks with the `#disqus_thread` anchor 
with the current comment count.

    <a href="{{ object.get_absolute_url }}#disqus_thread">View Comments</a>

Include the templatetag at the bottom of your website before the closing 
`</body>` tag:

    {% load disqus_tags %}
    {% disqus_num_replies %}

#### **disqus\_show\_comments** 

Include the templatetag in your HTML where you'd like the comments to appear.

    {% load disqus_tags %}
    {% disqus_show_comments %}

## Troubleshooting

Make sure that:

* Each content object has a get\_absolute\_url() method.
* Your Site has the correct domain set.
* The content object has a __unicode__ method

## TODO

* `is_usable` for templatetags
