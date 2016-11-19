import requests
import lassie
from flask import render_template, render_template_string
import tasks
from app import cli, redis_cache


def cache_request(urls):
    print "urls sent to queue"
    return tasks.cache_urls.delay(urls)


def get_content(url):
    if redis_cache.get(url):
        resp = redis_cache.get(url)
        print type(resp), "item loaded from cache"
    else:
        resp = cli.oembed(url, words = 30)
        redis_cache.set(url, jsonify(resp))
    print resp
    if resp.get("provider_name") == "Twitter":
        return render_twitter(url)
    elif resp.get("provider_name") == "YouTube":
        return render_youtube(resp.get("html"))
    elif resp["type"] == "rich":
        print "rich"
        ratio = (float(resp.get("height",1))/resp.get("width",1))*100
        print ratio
        if ratio <= 0:
            ratio = 100
        return render_template("video.html", content = resp.get("html"), ratio = str(ratio))
    elif resp["type"] == "video":
        print "video"
        ratio = (float(resp.get("height", 1))/resp.get("width",1))*100
        print ratio
        if ratio <= 0:
            ratio = 100
        return render_template("video.html", content = resp.get("html"), ratio = ratio)
    elif resp["type"] == "link":
        return render_template("article.html", title = resp.get("title"), image=resp.get("thumbnail_url"), description = resp.get("description"), _url=resp.get("url"))
    elif resp["type"]  == "photo":
        print "photo"
        return render_template("photo.html", _url = str(resp["url"]), source = resp.original_url)
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
    resp = lassie.fetch(url)
    thumbnail = resp.get('images')[0].get('src')
    title = resp.get('title')
    description = resp.get('description')
    return render_template('article.html', image = thumbnail, title = title, description = description)
