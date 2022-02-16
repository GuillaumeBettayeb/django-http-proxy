import logging

import urllib2
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.views.generic import View

from httpproxy import settings

logger = logging.getLogger(__name__)


class CacheMixin(object):
    cache_timeout = 60

    def get_cache_timeout(self):
        return self.cache_timeout

    def dispatch(self, *args, **kwargs):
        return cache_page(self.get_cache_timeout())(
            super(CacheMixin, self).dispatch)(*args, **kwargs)


class HttpProxy(View):
    mode = None
    base_url = "http://" + settings.PROXY_DOMAIN
    msg = 'Response body: \n%s'

    def get_protocol(self, request):
        if request.HttpRequest.is_secure():
            return "https://"
        else:
            return "http://"

    def dispatch(self, request, url, *args, **kwargs):
        self.url = url
        request = self.normalize_request(request)
        response = super(HttpProxy, self).dispatch(request, *args, **kwargs)
        return response

    def normalize_request(self, request):
        """
        Updates all path-related info in the original request object with the url
        given to the proxy

        This way, any further processing of the proxy'd request can just ignore
        the url given to the proxy and use request.path safely instead.
        """
        if not self.url.startswith('/'):
            self.url = '/' + self.url
        request.path = self.url
        request.path_info = self.url
        request.META['PATH_INFO'] = self.url
        return request

    def get(self, request, *args, **kwargs):
        request_url = self.get_full_url(self.url)
        request = self.create_request(request_url)
        response = urllib2.urlopen(request)
        try:
            response_body = response.read()
            status = response.getcode()
            logger.debug(self.msg % response_body)
        except urllib2.HTTPError as e:
            response_body = e.read()
            logger.error(self.msg % response_body)
            status = e.code
        return HttpResponse(response_body, status=status,
                            content_type=response.headers['content-type'])

    def get_full_url(self, url):
        """
        Constructs the full URL to be requested
        """
        param_str = self.request.GET.urlencode()
        request_url = u'%s%s' % (self.base_url, url)
        request_url += '?%s' % param_str if param_str else ''
        return request_url

    def create_request(self, url, body=None, headers={}):
        request = urllib2.Request(url, body, headers)
        logger.info('%s %s' % (request.get_method(), request.get_full_url()))
        return request


proxy = HttpProxy.as_view()
