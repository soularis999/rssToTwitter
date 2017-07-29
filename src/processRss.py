#!/usr/bin/python
"""
Purpose of the script is to poll the services for updates, compare the updates to the stored data and publish the
updates to twitter
"""
import logging
import sys
import getopt

from data_store import FileBasedDataStore, S3BasedDataStore, STORE
from feedparser import parse
from twitter_post import TwitterPost
from feed_config import Config
from datetime import datetime

log = logging.getLogger(__name__)


def get_id_from_post(post):
    """
    Given the post the method returns the derived id of the post
    :param post: post
    :return: id
    """
    title = post['title'].encode('utf-8') if 'title' in post and post['title'] else None
    url = post['link'].encode('utf-8') if 'link' in post and post['link'] else title
    return post['id'].encode('utf-8') if 'id' in post and post['id'] else url


def cleanup_feeds(store, num_posts, entries):
    """
    Given the list of entries the method will return the trimmed list of posts that can be published
    The filtering comprises of limiting the posts to only those that were not published and limiting to max configured
    number of posts for the particular service. Assumption is that the posts are already sorted from most recent to most
    furthest
    :param conf_data:
    :param entries:
    :return:
    """
    if not entries:
        return []

    first_post = min(len(entries), num_posts if num_posts else len(entries))
    if store:
        for index, post in enumerate(entries[:first_post]):
            if store.lastProcessedId == get_id_from_post(post):
                first_post = index
                break

    return reversed(entries[:first_post])


def parse_published_date(post):
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
    date = (parse_published_date(post) - datetime.utcfromtimestamp(0)).total_seconds()

    key = (conf_data, id, date)
    return tp.prepare(key, title, url)


def process(dry_run=False, store_type=0, *files):
    """
    Given the config files the method coordinates the retrieval of the data and publishing it to twitter
    :param dry_run: is this a test run - in this case data will be read but not published to twitter and store will not
        be updated
    :param files: config files
    """
    config = Config(*files)
    mainConfig = config.globalConfig("MAIN")
    twitter = config.globalConfig("TWITTER")
    aws = config.globalConfig("AWS")

    store = FileBasedDataStore(mainConfig, dry_run) if 0 == store_type else S3BasedDataStore(mainConfig, aws, dry_run)
    tp = TwitterPost(twitter, dry_run)

    num_items = 0
    for service in config.services():
        conf_data = config[service]
        store_record = store[service]
        log.info("Processing service %s -> %s" % (service, conf_data))

        feeds = parse(conf_data.url)
        if 'status' not in feeds or feeds['status'] is not 200:
            log.error("Error getting feeds %s -> %s" % (conf_data.url, feeds))
            continue

        for post in cleanup_feeds(store_record, conf_data.numPosts, feeds['entries']):
            if num_items >= mainConfig.numToProcessAtOneTime:
                break

            if process_posts(conf_data, post, tp):
                num_items += 1

        if num_items >= mainConfig.numToProcessAtOneTime:
            break

    log.info("Processed %i items " % num_items)

    # get results dict indexed by (service id / post id) key
    results = tp.post()

    filtered_services = {}
    for key in sorted(results.keys(), key=lambda key: key[2], reverse=True):
        log.debug("Keys %s -> %s" % (key, results[key]))
        (conf_data, post_id, date) = key[:3]
        if conf_data not in filtered_services or filtered_services[conf_data][2] < date:
            filtered_services[conf_data] = key

    for conf_data, item in filtered_services.iteritems():
        store[conf_data.serviceName] = STORE(conf_data.serviceName, item[1], item[2])

    # in the end - write the store
    store.write_store()


def usage():
    print """Usage: processRss -d <config files>
             Where:
             -d | --dryrun: do not publish to twitter - just get data and update the store
             -v | --verbose: the verbose output
             -h | --help: help
             
             <config files> - the list of config files to use
             """


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "dht:v", ["dryRun", "help", "type", "verbose"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print str(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    isDryRun = False
    logLevel = logging.INFO
    store_type = 0
    for option, var in opts:
        if option in ("-h", "--help"):
            usage()
            sys.exit()
        elif option in ("-d", "--dryrun"):
            isDryRun = True
        elif option in ("-t", "--type"):
            store_type = int(var)
        elif option in ("-v", "--verbose"):
            logLevel = logging.DEBUG

    logging.basicConfig(level=logLevel)
    process(isDryRun, store_type, *args)


if __name__ == "__main__":
    main()
