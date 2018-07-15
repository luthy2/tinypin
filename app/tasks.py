from app import app, cli, redis_cache, celery
import json




@celery.task
def cache_urls(urls):
    #check which urls are not in the cache
    not_cached_urls = []
    for u in urls:
        r = redis_cache.get(u)
        if not r :
            not_cached_urls.append(u)

    #takes a list and splits it into a list of lists of size n
    def chunks(u, n= 20):
        for i in xrange(0,len(urls),n):
            yield urls[i:i+n]

    #send each batch to the embedly api and cache the results
    for batch in list(chunks(not_cached_urls)):
        resp = cli.oembed(batch, raw = True, words=30)
        for i in resp:
            c = redis_cache.set(i.get(original_url), i.get('raw'))
        print 'Item cached', c
    return True
