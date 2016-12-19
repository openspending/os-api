import logging
import os

import datadog


def setup_stats(app):
    statsd_host = os.environ.get('OS_STATSD_HOST', 'localhost')
    stats = datadog.DogStatsd(host=statsd_host)
    app.extensions['stats'] = stats

    logging.info('STATSD HOST %s', statsd_host)
    return stats

