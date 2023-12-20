#!/usr/bin/env python3
""" Module for Redis db """
import redis
from uuid import uuid4
from typing import Union, Callable, Optional


UnionOfTypes = Union[str, bytes, int, float]


class Cache:
    """ Class for methods that operate a caching system """

    def __init__(self):
        """ Instance of the Redis db """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: UnionOfTypes) -> str:
        """
        Method takes a data argument and returns a string
        """
        self._key = str(uuid4())
        self._redis.set(self._key, data)
        return self._key

    def get(self, key: str,
            fn: Optional[Callable] = None) -> UnionOfTypes:
        """
        Retrieves data stored in redis using a key
        converts the result/value back to the desired format
        """
        value = self._redis.get(key)
        return fn(value) if fn else value

    def get_str(self, value: str) -> str:
        """ get a string """
        return self.get(self._key, str)

    def get_int(self, value: str) -> int:
        """ get an int """
        return self.get(self._key, int)

    def count_calls(method: Callable) -> Callable:
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            key = f"{method.__qualname__}"
            self.redis.incr(key)
            return method(self, *args, **kwargs)
        return wrapper

    def call_history(method: Callable) -> Callable:
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            key_inputs = f"{method.__qualname__}:inputs"
            key_outputs = f"{method.__qualname__}:outputs"

        # Store input arguments
        self.redis.rpush(key_inputs, str(args))

        # Execute the wrapped function
        output = method(self, *args, **kwargs)

        # Store output result
        self.redis.rpush(key_outputs, str(output))

        return output

    def replay(method: Callable) -> None:
        # Assuming your redis instance is already initialized
        r = redis.Redis()

        # Get the qualified name of the method
        method_name = method.__qualname__

        # Get the keys for inputs and outputs
        inputs_key = f"{method_name}:inputs"
        outputs_key = f"{method_name}:outputs"

        # Get the inputs and outputs lists
        inputs = r.lrange(inputs_key, 0, -1)
        outputs = r.lrange(outputs_key, 0, -1)

        # Display the history of calls
        print(f"{method_name} was called {len(inputs)} times:")
        for inp, out in zip(inputs, outputs):
            print(f"{method_name}(*{inp.decode()}) -> {out.decode()}"
