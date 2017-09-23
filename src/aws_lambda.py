import logging
import sys

from process_rss import process

def lambda_handler(event, context):
    dry_run = "DRYRUN" in event
    is_aws = "IS_AWS" in event
    log_level = logging.DEBUG if "VERBOSE" in event else logging.INFO
    files = event["FILES"]

    logging.basicConfig(level=log_level)

    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
    logging.getLogger().addHandler(h)

    log = logging.getLogger(__name__)
    log.debug("In lambda handler -> %s %s %s" % (dry_run, is_aws, files))

    return process(dry_run, is_aws, *files)
