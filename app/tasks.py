from app import app, cli, redis_cache, celery




@celery.task
def cache_urls(urls):
  not_cached_urls = []
  for u in urls:
    rv = redis_cache.get(u)
    if not rv:
      not_cached_urls.append('u')
  resp = cli.oembed(not_cached_urls, words=30)
  for i in resp:
      c = redis_cache.set(i["original_url"], i)
      print 'Item cached in Redis', c
  return True
