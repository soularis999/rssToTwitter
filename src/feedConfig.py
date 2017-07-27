import configparser
import logging
import os

from collections import namedtuple

log = logging.getLogger(__name__)

SERVICE = namedtuple("Service", "serviceName url numPosts store")
STORE = namedtuple("Store", "serviceName lastProcessedId lastProcessedUpdateTimestamp")
MAIN = namedtuple("Main",
                  "numToProcessAtOneTime appTwitterKey appTwitterSecret userTwitterKey userTwitterSecret")


class Config(object):
    """
    Purpose of the class is to keep information about configurations
    """

    def __init__(self, dry_run=False, store_path="~/.twStore"):
        self._services = {}
        self._store = {}
        self._main = None
        self._dry_run = dry_run
        self._store_path = store_path
        pass

    def open(self, *files):
        config = configparser.ConfigParser()
        for configFile in files:
            log.info("reading config file %s" % configFile)
            config.read(os.path.expanduser(configFile))

        store_data = self._readStore()
        self._readConfig(config, store_data)
        self._validate()

    def _readConfig(self, config, storeData):
        for section in config.sections():
            section_name = Config._encode(section)
            log.info("configuring section %s" % section_name)

            if section_name == "MAIN":
                self._main = MAIN(
                    int(config.get(section, 'num_process_at_one_time')) if config.has_option(section,
                                                                                             'num_process_at_one_time') else 15,
                    config.get(section, 'application_twitter_key'),
                    config.get(section, 'application_twitter_secret'),
                    config.get(section, 'user_twitter_key'),
                    config.get(section, 'user_twitter_secret'))
            else:
                service = SERVICE(
                    section_name,
                    config.get(section, 'url'),
                    config.getint(section, "numPosts") if config.has_option(section, "numPosts") else None,
                    storeData[section] if section in storeData else None
                )
                self._services[section_name] = service
                log.debug("Service %s" % (self._services[section_name],))

    def __getitem__(self, section):
        """
        Given the section the method returns a map of values
        :param section: section to search
        :return: values
        """
        return self._services[Config._encode(section)]

    def __setitem__(self, section, service):
        """
        Given the section and a service information the method will update the data in store
        :param section: section to search
        :return: values
        """
        self._services[Config._encode(section)] = service

    def services(self):
        """
        The method gets the set of sections to return
        :return: SERVICE object for the section requested
        """
        return self._services.keys()

    def mainService(self):
        return self._main

    def _readStore(self):
        """
        Read the last updated records from store
        :return dict of store objects indexed by service name
        """
        store = {}
        f_path = os.path.expanduser(self._store_path)
        log.debug("processing store %s" % f_path)

        if not os.path.exists(f_path):
            return store

        with file(f_path, 'r') as f:
            for line in f:
                data = line.strip().split("|")
                section_name = Config._encode(data[0])

                time = long(data[2]) if data[2] else None
                last_id = data[1] if data[1] else None
                if time and last_id:
                    record = STORE(section_name, data[1], time)
                    log.debug("processing store record %s" % (record,))
                    store[section_name] = record
                else:
                    log.error("Could not parse the record for %s" % line)
                    store[section_name] = None
        return store

    def writeStore(self):
        """
        After the services were updated with latest information the writeStore has to be called to persists the
        data into the file. The file will be read on startup
        :return:
        """
        f_path = os.path.expanduser(self._store_path)
        log.debug("writing store %s" % f_path)

        count = 0
        if not self._dry_run:

            store_data = self._readStore()
            with file(f_path, 'w') as f:

                def writeFunc(service_name, store, file):
                    id = store.lastProcessedId if store.lastProcessedId else ''
                    time = store.lastProcessedUpdateTimestamp if store.lastProcessedUpdateTimestamp else ''
                    text = '%s|%s|%s\n' % (service_name, id, time)
                    file.write(text)

                    if service_name in store_data:
                        del store_data[service_name]

                    return text

                # The chain does
                # 1. scan all items in _service dict and gets all service names where store was populated or None
                # 2. filters out None values
                # 3. applied function writeFunc with remaining service_names
                result_text = map(lambda sname: writeFunc(sname, self._services[sname].store, f),
                                  filter(lambda sname: sname, map(
                                      lambda (sname, value): sname if value.store else None,
                                      self._services.iteritems())))
                count = len(result_text)

                # this chain applies the remaining stored data so we would not start reposting the old posts if
                # old service was reenabled
                result_text = map(lambda sname, store: writeFunc(sname, store, f), store_data.iteritems())

                count += len(result_text)

        log.info("Saved %i records" % count)

    def _validate(self):
        if not self._main:
            raise SystemError("Main config was not populated")

    @staticmethod
    def _encode(section):
        return str(section).upper().strip()
