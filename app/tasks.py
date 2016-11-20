from app import app, cli, redis_cache, celery
import json



@celery.task
def cache_urls(urls):
  not_cached_urls = []
  for u in urls:
    r = redis_cache.get(u)
    if not r:
      not_cached_urls.append(u)
  resp = cli.oembed(not_cached_urls, raw = True, words=30)
  for i in resp:
      c = redis_cache.set(i["original_url"], i['raw'])
      print 'Item cached', c
  return True
