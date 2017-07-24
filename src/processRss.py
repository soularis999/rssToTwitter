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

DRY_RUN = True

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def process(*files):
    config = Config()
    config.open(*files)

    tp = TwitterPost(config.mainService().appTwitterKey, config.mainService().appTwitterSecret, DRY_RUN)

    num_items = 0
    for service in config.services():
        log.info("Service: %s" % service)
        conf_data = config[service]
        feeds = parse(conf_data.url)
        if 'status' not in feeds or feeds['status'] is not 200:
            log.error("Error getting data for %s -> %s" % (conf_data.url, feeds))
            continue

        newest_id = published_date = None
        for post in cleanup_feeds(conf_data, feeds['entries']):
            if num_items >= config.mainService().numToProcessAtOneTime:
                break
            newest_id, published_date = process_posts(config, post, tp)
            num_items += 1

        if newest_id and published_date:
            config[service] = SERVICE(conf_data.url, conf_data.numPosts, newest_id, published_date)

        if num_items > config.mainService().numToProcessAtOneTime:
            break

    log.info("Processed %i items " % num_items)
    config.writeStore()


def cleanup_feeds(conf_data, entries):
    if not entries:
        return []

    first_post = min(len(entries), conf_data.numPosts if conf_data.numPosts else len(entries))
    if conf_data.lastProcessedId:
        for index, post in enumerate(entries[:first_post]):
            if conf_data.lastProcessedId == post['id']:
                first_post = index
                break

    return reversed(entries[:first_post])


def process_posts(config, post, tp):
    title = post['title'].encode('utf-8') if 'title' in post and post['title'] else None
    url = post['link'].encode('utf-8') if 'link' in post and post['link'] else None
    text = generatePost(title, url)

    if text:
        tp.post(config.mainService().userTwitterKey, config.mainService().userTwitterSecret, text)

    newest_id = post['id'].encode('utf-8')
    date = datetime(post['published_parsed'].tm_year, post['published_parsed'].tm_mon,
                    post['published_parsed'].tm_mday, post['published_parsed'].tm_hour,
                    post['published_parsed'].tm_min, post['published_parsed'].tm_sec)
    published_date = long((date - datetime.utcfromtimestamp(0)).total_seconds())

    return newest_id, published_date


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


if __name__ == "__main__":
    files = sys.argv[1:]
    process(*files)
