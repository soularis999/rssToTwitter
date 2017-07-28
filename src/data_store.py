import logging
import os
import util

from collections import namedtuple

log = logging.getLogger(__name__)

STORE = namedtuple("Store", "serviceName lastProcessedId lastProcessedUpdateTimestamp")


class DataStore(object):
    def __init__(self, dry_run=False):
        self._dry_run = dry_run
        self._stores = {}

    def __setitem__(self, section, store):
        """
        Given the section and a service information the method will update the data in store.
        Will raise SystemError if None is passed as section or service
        :param section: section to search
        :return: values
        """
        if not section:
            raise SystemError("Section name is empty")
        if not store:
            raise SystemError("Store is empty for %s" % section)

        self._stores[util.encode(section)] = store

    def __getitem__(self, section):
        """
        Given the section the method returns a map of values
        :param section: section to search
        :return: values
        """
        return self._stores[util.encode(section)]

    def __len__(self):
        """
        returns the number of configured services
        :return:
        """
        return len(self._stores)

    def __str__(self):
        return self._stores.__str__()


class FileBasedDataStore(DataStore):
    def __init__(self, dry_run=False, store_path="~/.twStore"):
        DataStore.__init__(self, dry_run)
        self._store_path = store_path
        self._read_store()

    def _read_store(self):
        """
        Read the last updated records from store
        :return dict of store objects indexed by service name
        """
        self._stores = {}
        f_path = os.path.expanduser(self._store_path)
        log.info("reading store %s" % f_path)

        if not os.path.exists(f_path):
            return

        with file(f_path, 'r') as f:
            for line in f:
                data = line.strip().split("|")
                section_name = util.encode(data[0])

                time = long(data[2]) if data[2] else None
                last_id = data[1] if data[1] else None
                if time and last_id:
                    record = STORE(section_name, data[1], time)
                    log.debug("processing store record %s" % (record,))
                    self._stores[section_name] = record
                else:
                    log.error("Could not parse the record for %s" % line)
                    self._stores[section_name] = None

    def write_store(self, result_text=None):
        """
        After the services were updated with latest information the writeStore has to be called to persists the
        data into the file. The file will be read on startup
        :param result_text the list item that will be populated with text writen to file
        :return: number of items written
        """
        f_path = os.path.expanduser(self._store_path)
        log.info("writing store %s" % f_path)

        result_text = [] if result_text is None else result_text
        if not self._dry_run:
            with file(f_path, 'w') as f:
                def write(service_name, store, file):
                    post_id = store.lastProcessedId if store.lastProcessedId else ''
                    time = '%i' % store.lastProcessedUpdateTimestamp if store.lastProcessedUpdateTimestamp else ''
                    text = '%s|%s|%s\n' % (service_name, post_id, time)
                    file.write(text)

                    return text

                # write everything in store
                result_text = map(lambda sname: write(sname, self._stores[sname], f), self._stores.keys())

        log.info("Saved %i records" % len(result_text))
        return len(result_text)