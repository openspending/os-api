import json

from redis import StrictRedis

from .base_cache import BaseCache


class RedisCache(BaseCache):

    def __init__(self, redis_host, redis_port,
                 default_timeout):
        super(RedisCache, self).__init__(default_timeout=default_timeout)
        self.redis_connection = StrictRedis(host=redis_host, port=redis_port, db=1)

    def _put(self, context, params, item, timeout):
        key = RedisCache._make_key(context, params)
        self.redis_connection.set(key, item, ex=timeout)
        context_key = RedisCache._make_context_key(context)
        self.redis_connection.sadd(context_key, key)

    def _get(self, context, params):
        key = RedisCache._make_key(context, params)
        context_key = RedisCache._make_context_key(context)
        item = self.redis_connection.get(key)
        if item is None:
            self.redis_connection.srem(context_key, key)
        return item

    def _clear(self, context):
        context_key = RedisCache._make_context_key(context)
        pipe = self.redis_connection.pipeline()
        item = self.redis_connection.spop(context_key)
        while item is not None:
            pipe.delete(item)
            item = self.redis_connection.spop(context_key)

        pipe.execute(raise_on_error=False)

    @staticmethod
    def _make_key(context, params):
        params = json.dumps(params, ensure_ascii=True, sort_keys=True)
        return '{}:{}'.format(context, params)

    @staticmethod
    def _make_context_key(context):
        return RedisCache._make_key('ctx', context)