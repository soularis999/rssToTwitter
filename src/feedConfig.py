import configparser
import logging
import os

from collections import namedtuple

log = logging.getLogger(__name__)

SERVICE = namedtuple("Service", "url numPosts lastProcessedId lastProcessedUpdateTimestamp")
MAIN = namedtuple("Main", "storePath appTwitterKey appTwitterSecret userTwitterKey userTwitterSecret")

class Config(object):
    """
    Purpose of the class is to keep information about configurations
    """

    def __init__(self):
        self._services = {}
        self._store = {}
        self._main = None
        pass

    def open(self, *files):
        config = configparser.ConfigParser()
        for configFile in files:
            log.info("reading config file %s" % configFile)
            config.read(os.path.expanduser(configFile))

        self._readConfig(config)
        self._validate()
        self._readStore()

    def _readConfig(self, config):
        for section in config.sections():
            section_name = Config._encode(section)
            log.info("processing section %s" % section_name)

            if section_name == "MAIN":
                self._main = MAIN(
                    config.get(section, 'store_path') if config.has_option(section, 'store_path') else "~/.twStore",
                    config.get(section, 'application_twitter_key'),
                    config.get(section, 'application_twitter_secret'),
                    config.get(section, 'user_twitter_key'),
                    config.get(section, 'user_twitter_secret'))
            else:
                service = SERVICE(
                    config.get(section, 'url'),
                    config.getint(section, "numPosts") if config.has_option(section, "numPosts") else None,
                    None,
                    None
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
        Read the last updated records and update services to record it
        :param storePath:
        """
        f_path = os.path.expanduser(self._main.storePath)
        log.debug("processing store %s" % f_path)

        if not os.path.exists(f_path):
            return

        with file(f_path, 'r') as f:
            for line in f:
                data = line.split("|")
                key = Config._encode(data[0])

                if key in self._services.keys():
                    self._services[key] = SERVICE(
                        self._services[key].url,
                        self._services[key].numPosts,
                        data[1],
                        long(data[2])
                    )
                    log.debug("processing store record %s" % (self._services[key],))

    def writeStore(self):
        """
        After the services were updated with latest information the writeStore has to be called to persists the
        data into the file. The file will be read on startup
        :return:
        """
        f_path = os.path.expanduser(self._main.storePath)
        log.debug("writing store %s" % f_path)

        count = 0
        with file(f_path, 'w') as f:
            for line in filter(lambda v: v, map(
                    lambda (key, value):
                            '%s|%s|%s\n' % (key, value.lastProcessedId,
                                            value.lastProcessedUpdateTimestamp)
                    if value.lastProcessedId and value.lastProcessedUpdateTimestamp else None,
                    self._services.iteritems())):
                count += 1
                log.debug("Writing %s" % line)
                f.write(line)

        log.info("Saved %f records" % count)

    def _validate(self):
        if not self._main:
            raise SystemError("Main config was not populated")

    @staticmethod
    def _encode(section):
        return str(section).upper().strip()
