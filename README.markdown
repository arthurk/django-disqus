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

The following templatetags are available:
    
- **disqus\_dev**: Returns js that sets variables to display comments on local dev server
- **disqus\_num\_replies**: Returns js to display comment count
- **disqus\_show\_comments**: Returns js to display comment form
    
## Troubleshooting

Make sure that:

* Each content object has a get\_absolute\_url() method.
* Your Site has the correct domain set.
* The content object has a __unicode__ method

## TODO

* `is_usable` for templatetags
