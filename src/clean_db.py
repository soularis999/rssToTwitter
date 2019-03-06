import logging
import sys
import getopt
import dateutil.relativedelta

from datetime import datetime
from time import mktime
from data_store import DBBasedDataStore
from feed_config import Config

log = logging.getLogger(__name__)

def process(dry_run=False, *data):
    config = Config()
    db = config.globalConfig("DB")
    store = DBBasedDataStore(db, dry_run)
    days = int(data[0])

    log.info("Audit log cleanup for %s " % days)
    store.clean_audit_log(days)

def usage():
    print("""Usage: clean_db -d <days back>
             Where:
             -d | --dryrun: do not publish to twitter - just get data and update the store
             -v | --verbose: the verbose output
             -h | --help: help
             
             <days back> - how many days back to save
             """)
    
def main(params):
    try:
        opts, args = getopt.getopt(params, "dh:v", ["dryRun", "help", "verbose"])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    is_dry_run = False
    log_level = logging.INFO
    for option, var in opts:
        if option in ("-h", "--help"):
            usage()
            sys.exit()
        elif option in ("-d", "--dryrun"):
            is_dry_run = True
        elif option in ("-v", "--verbose"):
            log_level = logging.DEBUG

    logging.basicConfig(level=log_level)
    process(is_dry_run, *args)
    
if __name__ == "__main__":
    main(sys.argv[1:])
