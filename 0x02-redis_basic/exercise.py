#!/usr/bin/env python3
""" Module for Redis db """


import redis
import functools
from uuid import uuid4
from typing import Union, Callable, Optional


UnionOfTypes = Union[str, bytes, int, float]


class Cache:
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: UnionOfTypes) -> str:
        self._key = str(uuid4())
        self._redis.set(self._key, data)
        return self._key

    def get(self, key: str, fn: Optional[Callable] = None) -> UnionOfTypes:
        value = self._redis.get(key)
        return fn(value) if fn else value

    def get_int(self, value: str) -> int:
        return self.get(self._key, int)

    @staticmethod
    def count_calls(method: Callable) -> Callable:
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            key = f"{method.__qualname__}"
            self.redis.incr(key)
            return method(self, *args, **kwargs)
        return wrapper

    @staticmethod
    def call_history(method: Callable) -> Callable:
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            key_inputs = f"{method.__qualname__}:inputs"
            key_outputs = f"{method.__qualname__}:outputs"

            self.redis.rpush(key_inputs, str(args))
            output = method(self, *args, **kwargs)
            self.redis.rpush(key_outputs, str(output))

            return output
        return wrapper

    @staticmethod
    def replay(method: Callable) -> None:
        r = redis.Redis()

        method_name = method.__qualname__
        inputs_key = f"{method_name}:inputs"
        outputs_key = f"{method_name}:outputs"

        inputs = r.lrange(inputs_key, 0, -1)
        outputs = r.lrange(outputs_key, 0, -1)

        print(f"{method_name} was called {len(inputs)} times:")
        for inp, out in zip(inputs, outputs):
            print(f"{method_name}(*{inp.decode()}) -> {out.decode()}")
