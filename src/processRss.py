#!/usr/bin/python
"""
Purpose of the script is to poll the services for updates, compare the updates to the stored data and publish the
updates to twitter
"""
import logging
import sys
import getopt

from feedparser import parse
from twitterPost import TwitterPost
from feedConfig import Config, SERVICE
from datetime import datetime

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def get_id_from_post(post):
    title = post['title'].encode('utf-8') if 'title' in post and post['title'] else None
    url = post['link'].encode('utf-8') if 'link' in post and post['link'] else title
    return post['id'].encode('utf-8') if 'id' in post and post['id'] else url

def cleanup_feeds(conf_data, entries):
    if not entries:
        return []

    first_post = min(len(entries), conf_data.numPosts if conf_data.numPosts else len(entries))
    if conf_data.lastProcessedId:
        for index, post in enumerate(entries[:first_post]):
            if conf_data.lastProcessedId == get_id_from_post(post):
                first_post = index
                break

    return reversed(entries[:first_post])


def parse_published(post):
    """
    Parse publisher and return datetime object
    """
    if 'published_parsed' in post:
        return datetime(post['published_parsed'].tm_year, post['published_parsed'].tm_mon,
                        post['published_parsed'].tm_mday, post['published_parsed'].tm_hour,
                        post['published_parsed'].tm_min, post['published_parsed'].tm_sec)
    else:
        return datetime.now()


def process_posts(conf_data, post, tp):
    """
    Process the post - generating the text for twitter and the id that contains
    (service id, post id)
    :param conf_data: config data
    :param post: post
    :param tp: twitter publisher
    :return: true if prepare was successfull or False otherwise
    """
    title = post['title'].encode('utf-8') if 'title' in post and post['title'] else None
    url = post['link'].encode('utf-8') if 'link' in post and post['link'] else None
    id = get_id_from_post(post)
    date = long((parse_published(post) - datetime.utcfromtimestamp(0)).total_seconds())

    key = (conf_data, id, date)
    return tp.prepare(key, title, url)


def process(dryRun=False, *files):
    """
    Given the config files the method coordinates the retrieval of the data and publishing it to twitter
    :param dryRun: is this a test run - in this case data will be read but not published to twitter and store will not
        be updated
    :param files: config files
    """
    config = Config(dryRun)
    config.open(*files)

    tp = TwitterPost(config.mainService().appTwitterKey, config.mainService().appTwitterSecret, dryRun)
    num_items = 0
    for service in config.services():
        conf_data = config[service]
        feeds = parse(conf_data.url)
        if 'status' not in feeds or feeds['status'] is not 200:
            log.error("Error getting data for %s -> %s" % (conf_data.url, feeds))
            continue

        for post in cleanup_feeds(conf_data, feeds['entries']):
            if num_items >= config.mainService().numToProcessAtOneTime:
                break

            if process_posts(conf_data, post, tp):
                num_items += 1

        if num_items >= config.mainService().numToProcessAtOneTime:
            break

        log.info("Processed service %s " % service)

    log.info("Processed %i items " % num_items)

    # get results dict indexed by (service id / post id) key
    results = tp.post(config.mainService().userTwitterKey, config.mainService().userTwitterSecret)
    filtered_services = {}
    for item in sorted(filter(lambda key: results[key], results.keys()), key=lambda key: key[2], reverse=True):
        conf_data = item[0]
        date = item[2]
        if conf_data not in filtered_services or filtered_services[conf_data][2] < date:
            filtered_services[conf_data] = item

    for conf_data, item in filtered_services.iteritems():
        config[conf_data.serviceName] = SERVICE(conf_data.serviceName, conf_data.url, conf_data.numPosts, item[1],
                                                item[2])

    config.writeStore()


def usage():
    print """Usage: processRss -c <config files> -d
             Where:
             -c | -- config : comma delimited list of the config files
             -d | --dryrun: do not publish to twitter - just get data and update the store
             -h | --help: help
             """


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hdc:", ["help", "dryRun", "config"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    isDryRun = False
    conFileList = []
    for option, var in opts:
        if option in ("-h", "--help"):
            usage()
            sys.exit()
        elif option in ("-d", "--dryrun"):
            isDryRun = True
        elif option in ("-c", "--config"):
            conFileList = var.split(",")

    process(isDryRun, *conFileList)


if __name__ == "__main__":
    main()


