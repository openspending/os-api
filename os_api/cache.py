from urllib.parse import urlparse, parse_qs

from flask import current_app, request, url_for

from os_api_cache import get_os_cache


def service_for_path(path, query):
    for x in {'/aggregate', '/members/', '/facts', '/package', '/model', '/loader'}:
        if x in path:
            package_id = path.split(x)[0].split('/')[-1]
            if package_id == '2':
                qs = parse_qs(query)
                package_id = str(qs.get('dataset'))
            service = x.replace('/', '')
            return package_id, service
    return None, None


def return_cached():
    cache = current_app.extensions.get('cache')
    loader = current_app.extensions.get('loader')
    stats = current_app.extensions.get('stats')

    o = urlparse(request.url)
    stats.increment('openspending.api.requests')
    package_id, service = service_for_path(o.path, o.query)
    if service is not None:
        stats.increment('openspending.api.requests.' + service)

    if cache is not None \
            and not (loader and o.path.startswith(url_for('FDPLoader.load'))):
        response = cache.get_from_cache(package_id, o.query, o.path)
        if response:
            stats.increment('openspending.api.cache.hits')
            response.from_cache = True
            response.headers.add('X-OpenSpending-Cache', 'true')
            response.headers.add('X-OpenSpending-PackageId', package_id)
            return response
        stats.increment('openspending.api.cache.misses')


def cache_response(response):
    cache = current_app.extensions.get('cache')
    stats = current_app.extensions.get('stats')

    o = urlparse(request.url)
    stats.increment('openspending.api.responses.%d' % response.status_code)

    if cache is not None and response.status_code == 200 and not hasattr(response, 'from_cache'):
        package_id, _ = service_for_path(o.path)
        if package_id is not None:
            cache.put_in_cache(package_id, o.query, o.path, response)
            response.headers.add('X-OpenSpending-Cache', 'false')
            response.headers.add('X-OpenSpending-PackageId', package_id)
    return response


def setup_caching(app):
    cache = get_os_cache()
    if cache is not None:
        app.extensions['cache'] = cache

        app.before_request(return_cached)
        app.after_request(cache_response)
