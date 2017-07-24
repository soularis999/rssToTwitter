#!/usr/bin/python
"""
Purpose of the script is to poll the services for updates, compare the updates to the stored data and publish the
updates to twitter
"""
import logging
import sys

from feedparser import parse
from twitterPost import TwitterPost
from feedConfig import Config, SERVICE
from datetime import datetime

DRY_RUN = False

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def generatePost(data, url):
    text = ''
    if data:
        text = (data[:120] if len(data) > 120 else data) + ' '
    if url:
        text += url

    text = text.strip()
    if 0 == len(text):
        return None
    return text


def process(*files):
    config = Config()
    config.open(*files)

    tp = TwitterPost(config.mainService().appTwitterKey, config.mainService().appTwitterSecret, DRY_RUN)

    for service in config.services():
        conf_data = config[service]
        feeds = parse(conf_data.url)
        if feeds['status'] is not 200:
            log.error("Error getting data for %s" % (conf_data.url))
            continue

        newest_id, published_date = process_posts(conf_data, config, feeds, tp)
        if newest_id and published_date:
            config[service] = SERVICE(conf_data.url, conf_data.numPosts, newest_id, published_date)

    config.writeStore()


def process_posts(conf_data, config, feeds, tp):
    newest_id = None
    published_date = None
    for index, post in enumerate(feeds['entries']):
        if index >= conf_data.numPosts:
            break
        elif conf_data.lastProcessedId and conf_data.lastProcessedId == post['id']:
            break

        title = post['title'].encode('utf-8') if 'title' in post and post['title'] else None
        url = post['link'].encode('utf-8') if 'link' in post and post['link'] else None
        text = generatePost(title, url)

        if text:
            tp.post(config.mainService().userTwitterKey, config.mainService().userTwitterSecret, text)

        if not newest_id:
            newest_id = post['id'].encode('utf-8')
            date = datetime(post['published_parsed'].tm_year, post['published_parsed'].tm_mon,
                            post['published_parsed'].tm_mday, post['published_parsed'].tm_hour,
                            post['published_parsed'].tm_min, post['published_parsed'].tm_sec)
            published_date = long((date - datetime.utcfromtimestamp(0)).total_seconds())
    return newest_id, published_date


if __name__ == "__main__":
    files = sys.argv[1:]
    process(*files)
