Mini Django HTTP Proxy
=================

A stripped down and updated for django 1.6 version of django-http-proxy.
http://httpproxy.yvandermeer.net/

pip install and add to installed apps::

    INSTALLED_APPS = ('httpproxy', 
                          ...)

add proxy domain and optionally cache timeout to settings (default cache timeout is 60 seconds)::

    PROXY_DOMAIN = 'google.com'
    PROXY_CACHE_TIMEOUT = 120

Then make a url in urls.py that will forward requests::

    url(r'^my-google/(?P<url>.*)$', 'httpproxy.views.proxy'),


