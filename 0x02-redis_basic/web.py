#!/usr/bin/env python3
'''A module with tools for request caching and tracking.'''
import requests
import redis
import time

r = redis.StrictRedis()
'''The module-level Redis instance.'''


def track_url_count(func):
    def wrapper(url):
        r.incr(f"count:{url}")
        return func(url)
    return wrapper


@track_url_count
def get_page(url):
    cached_content = r.get(url)
    if cached_content:
        return cached_content.decode('utf-8')

    response = requests.get(url)
    content = response.text

    r.setex(url, 10, content)
    return content


if __name__ == "__main__":
    # Test the get_page function
    test_url = 'http://slowwly.robertomurray.co.uk/delay/10000/url/'
    test_url += 'http://www.google.co.uk'
    for _ in range(5):
        print(get_page(test_url))
        time.sleep(1)  # Delay to simulate separate calls
