from app import redis
from app import cli



@app.task
def cache_urls(urls):
  not_cached_urls = []
  for u in urls:
    rv = redis.get(u)
    if not rv:
      not_cached_urls.append('u')
  resp = cli.oembed(not_cached_urls, words=30)
  for i in resp:
      redis.set(i["original_url"], i)
  return True
