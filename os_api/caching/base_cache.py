import pickle

class BaseCache(object):

    def __init__(self, default_timeout):
        self._default_timeout = default_timeout

    def put(self, context, params, item, timeout=None):
        pickled = pickle.dumps(item)
        self._put(context, params, pickled, self.timeout(timeout))

    def get(self, context, params):
        pickled = self._get(context, params)
        if pickled is not None:
            return pickle.loads(pickled)

    def clear(self, context):
        self._clear(context)

    def timeout(self, _timeout=None):
        if _timeout is not None:
            return _timeout
        return self._default_timeout

    # Abstract methods
    def _get(self, **kwargs):
        raise NotImplementedError

    def _put(self, **kwargs):
        raise NotImplementedError

    def _clear(self, **kwargs):
        raise NotImplementedError

