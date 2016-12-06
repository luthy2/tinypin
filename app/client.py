import json
import requests
import lassie
from flask import render_template, render_template_string, jsonify
import tasks
from app import cli, redis_cache
from urlparse import urlparse

def cache_request(urls):
    print "urls sent to queue"
    return tasks.cache_urls.delay(urls)


def get_content(url):
    if redis_cache.get(url):
        resp = redis_cache.get(url)
        resp = json.loads(resp.decode('utf-8'))
        print resp, "item loaded from cache"
    else:
        resp = cli.oembed(url, raw=True, words = 30)
        if resp.get('raw'):
            r = redis_cache.set(url, resp.get('raw'))
            print 'item cached:', r
        else:
            resp = lassie.fetch(url)
            r = redis_cache.set(url, jsonify(resp))
    print resp
    if resp:
        if resp.get("provider_name") == "Twitter":
            return render_twitter(url)
        elif resp.get("provider_name") == "YouTube":
            return render_youtube(resp.get("html"))
        elif resp.get("type") == "rich":
            print "rich"
            ratio = (float(resp.get("height",1))/resp.get("width",1))*100
            print ratio
            if ratio <= 0:
                ratio = 100
            return render_template("video.html", content = resp.get("html"), ratio = str(ratio))
        elif resp.get("type") == "video":
            print "video"
            ratio = (float(resp.get("height", 1))/resp.get("width",1))*100
            print ratio
            if ratio <= 0:
                ratio = 100
            return render_template("video.html", content = resp.get("html"), ratio = ratio)
        elif resp.get("type") == "link":
            return render_template("article.html", title = resp.get("title"), image=resp.get("thumbnail_url"), description = resp.get("description"), _url=resp.get("url"), provider = resp.get("provider_name"))
        elif resp.get("type")  == "photo":
            print "photo"
            return render_template("photo.html", _url = str(resp["url"]), source = resp.original_url)
        else:
            return render_nostyle(url)
    else:
        return render_nostyle(url)

def render_twitter(url):
    query_url = "https://api.twitter.com/1.1/statuses/oembed.json"
    data = {"url":url}
    resp = requests.get(query_url, params=data)
    if resp.status_code == 200:
        r = resp.json()
        return r.get("html")
    else:
        print 'twitte pizza'

def render_youtube(html):
    return render_template("video.html", youtube = True, content = html)

def render_nostyle(url):
    resp = redis_cache.get(url)
    print resp, type(resp)
    if not resp:
        resp = lassie.fetch(url)
        resp = json.dumps(resp)
        r = redis_cache.set(url, resp)
    else:
        resp = json.loads(resp)
    thumbnail = resp.get('images')
    if thumbnail:
        thumbnail = thumbnail[0].get('src')
    title = resp.get('title')
    description = resp.get('description')
    parse_obj = urlparse(url)
    provider = parse_obj.netloc
    return render_template('article.html', _url = url, image = thumbnail, title = title, description = description, provider=provider)
