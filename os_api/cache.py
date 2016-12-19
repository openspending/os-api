import os
from urllib.parse import urlparse

import logging
from flask import current_app, request, url_for

from .caching.redis_cache import RedisCache


def service_for_path(path):
    for x in {'/aggregate', '/members/', '/facts', '/package', '/model', '/loader'}:
        if x in path:
            return path.split(x)[0], x.replace('/', '')
    return None, None


def return_cached():
    cache = current_app.extensions.get('cache')
    loader = current_app.extensions.get('loader')
    stats = current_app.extensions.get('stats')

    o = urlparse(request.url)
    stats.increment('openspending.api.requests')
    context, service = service_for_path(o.path)
    if service is not None:
        stats.increment('openspending.api.requests.' + service)

    if cache is not None \
            and not (loader and o.path.startswith(url_for('FDPLoader.load'))):
        response = cache.get(context, {'q': o.query, 'p': o.path})
        if response:
            stats.increment('openspending.api.cache.hits')
            response.from_cache = True
            response.headers.add('X-OpenSpending-Cache','true')
            return response
        stats.increment('openspending.api.cache.misses')


def cache_response(response):
    cache = current_app.extensions.get('cache')
    stats = current_app.extensions.get('stats')

    o = urlparse(request.url)
    stats.increment('openspending.api.responses.%d' % response.status_code)

    if cache is not None and response.status_code == 200 and not hasattr(response, 'from_cache'):
        context, _ = service_for_path(o.path)
        if context is not None:
            cache.put(context, {'q': o.query, 'p': o.path}, response)
            response.headers.add('X-OpenSpending-Cache', 'false')
    return response


def setup_caching(app):
    if 'OS_API_CACHE' in os.environ:
        host = os.environ.get('OS_API_CACHE')
        cache_timeout = int(os.environ.get('OS_API_CACHE_TIMEOUT', 86400))
        cache = RedisCache(host, 6379, cache_timeout)

        logging.error('CACHE %s', cache)
        logging.error('CACHE TIMEOUT %s', cache_timeout)

        app.extensions['cache'] = cache

        app.before_request(return_cached)
        app.after_request(cache_response)
