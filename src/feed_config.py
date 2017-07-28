import configparser
import logging
import os
import util

from collections import namedtuple

log = logging.getLogger(__name__)

SERVICE = namedtuple("Service", "serviceName url numPosts")
MAIN = namedtuple("Main", "numToProcessAtOneTime")
TWITTER = namedtuple("TwitterApp", "appTwitterKey appTwitterSecret userTwitterKey userTwitterSecret")

APP_TWITTER_KEY_ENV = "APP_TWITTER_KEY"
APP_TWITTER_SECRET_ENV = "APP_TWITTER_SECRET"
USER_TWITTER_KEY_ENV = "USER_TWITTER_KEY"
USER_TWITTER_SECRET_ENV = "USER_TWITTER_SECRET"


class Config(object):
    """
    Purpose of the class is to keep information about configurations
    """

    def __init__(self):
        self._services = {}
        self._main = MAIN(15)

        self._twitterApp = TWITTER(os.environ[APP_TWITTER_KEY_ENV] if APP_TWITTER_KEY_ENV in os.environ else None,
                                   os.environ[APP_TWITTER_SECRET_ENV] if APP_TWITTER_SECRET_ENV in os.environ else None,
                                   os.environ[USER_TWITTER_KEY_ENV] if USER_TWITTER_KEY_ENV in os.environ else None,
                                   os.environ[
                                       USER_TWITTER_SECRET_ENV] if USER_TWITTER_SECRET_ENV in os.environ else None)
        pass

    def open(self, *files):
        config = configparser.ConfigParser()
        for configFile in files:
            log.info("reading config file %s" % configFile)
            config.read(os.path.expanduser(configFile))

        self._read_config(config)
        self._validate()

    def _read_config(self, config):
        for section in config.sections():
            section_name = util.encode(section)
            log.info("configuring section %s" % section_name)

            if section_name == "MAIN":
                self._main = MAIN(int(config.get(section, 'num_process_at_one_time'))
                                  if config.has_option(section,
                                                       'num_process_at_one_time') else 15)
            else:
                service = SERVICE(
                    section_name,
                    config.get(section, 'url'),
                    config.getint(section, "numPosts") if config.has_option(section, "numPosts") else None
                )
                self._services[section_name] = service
                log.debug("Service %s" % (self._services[section_name],))

    def __getitem__(self, section):
        """
        Given the section the method returns a map of values
        :param section: section to search
        :return: values
        """
        return self._services[util.encode(section)]

    def services(self):
        """
        The method gets the set of sections to return
        :return: SERVICE object for the section requested
        """
        return self._services.keys()

    def mainService(self):
        """
        Get the main app config
        :return:
        """
        return self._main

    def appService(self, type):
        """
        Given the type of service to return the method will get the service
        :param type: "TWITTER"
        :return: namedtuple for particular service
        """
        return self._twitterApp

    def _validate(self):
        twitterError = None
        if not self._twitterApp.appTwitterKey:
            twitterError = "app key"

        if not self._twitterApp.appTwitterSecret:
            twitterError = (twitterError + "," if twitterError else "") + "app secret"

        if not self._twitterApp.userTwitterKey:
            twitterError = (twitterError + "," if twitterError else "") + "user key"

        if not self._twitterApp.userTwitterSecret:
            twitterError = (twitterError + "," if twitterError else "") + "user secret"

        if twitterError:
            raise SystemError(
                "Twitter app was not configured (%s). Did you setup the env variables as defined in README?" %
                twitterError)
