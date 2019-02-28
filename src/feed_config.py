import configparser
import logging
import os
import util

from collections import namedtuple

log = logging.getLogger(__name__)

MAIN = namedtuple("Main", "numToProcessAtOneTime storeFileName")
SERVICE = namedtuple("Service", "serviceName url numPosts")
AWS_STORAGE = namedtuple("AWS", "awsAccessKey awsAccessSecret awsBucket awsFileName")
TWITTER = namedtuple("TwitterApp", "appTwitterKey appTwitterSecret userTwitterKey userTwitterSecret")
DB = namedtuple("DB", "url sslmode")

APP_TWITTER_KEY_ENV = "APP_TWITTER_KEY"
APP_TWITTER_SECRET_ENV = "APP_TWITTER_SECRET"
USER_TWITTER_KEY_ENV = "USER_TWITTER_KEY"
USER_TWITTER_SECRET_ENV = "USER_TWITTER_SECRET"

AWS_KEY_ENV = "AWS_KEY"
AWS_SECRET_ENV = "AWS_SECRET"
AWS_S3_BUCKET_ENV = "AWS_S3_BUCKET"
AWS_S3_STORE_FILE_NAME_ENV = "AWS_S3_STORE_FILE_NAME"

TWEETS_AT_ONE_TIME_ENV = "TWEETS_AT_ONE_TIME"
STORE_FILE_NAME_ENV = "STORE_FILE_NAME"

DATABASE_URL = "DATABASE_URL"
SSL_MODE = "SSL_MODE"

DEFAULT_STORE_PATH = "~/.twStore"
DEFAULT_S3_BUCKET = "rsstotwitter"
DEFAULT_AWS_S3_STORE_FILE_NAME = ".twStore"

class Config(object):
    """
    Purpose of the class is to keep information about configurations
    """

    def __init__(self, *files):
        self._services = {}

        self._main = MAIN(int(os.environ[TWEETS_AT_ONE_TIME_ENV]) if TWEETS_AT_ONE_TIME_ENV in os.environ else 15,
                          os.path.expanduser(
                              os.environ[
                                  STORE_FILE_NAME_ENV] if STORE_FILE_NAME_ENV in os.environ else DEFAULT_STORE_PATH))

        aws_store_file_name = os.environ[AWS_S3_STORE_FILE_NAME_ENV] \
            if AWS_S3_STORE_FILE_NAME_ENV in os.environ \
            else DEFAULT_AWS_S3_STORE_FILE_NAME

        self._aws = AWS_STORAGE(os.environ[AWS_KEY_ENV] if AWS_KEY_ENV in os.environ else None,
                                os.environ[AWS_SECRET_ENV] if AWS_SECRET_ENV in os.environ else None,
                                os.environ[AWS_S3_BUCKET_ENV] if AWS_S3_BUCKET_ENV in os.environ else DEFAULT_S3_BUCKET,
                                aws_store_file_name
                                )

        self._twitterApp = TWITTER(os.environ[APP_TWITTER_KEY_ENV] if APP_TWITTER_KEY_ENV in os.environ else None,
                                   os.environ[APP_TWITTER_SECRET_ENV] if APP_TWITTER_SECRET_ENV in os.environ else None,
                                   os.environ[USER_TWITTER_KEY_ENV] if USER_TWITTER_KEY_ENV in os.environ else None,
                                   os.environ[
                                       USER_TWITTER_SECRET_ENV] if USER_TWITTER_SECRET_ENV in os.environ else None)

        self._db = DB(os.environ[DATABASE_URL] if DATABASE_URL in os.environ else None,
                      "true" == os.environ[SSL_MODE] if SSL_MODE in os.environ else False)
        
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
        return list(self._services.keys())

    def globalConfig(self, type):
        """
        Get the config based on the type
        type: MAIN, TWITTER, AWS
        otherwise SystemError will be raised
        :return: config
        """
        if type is "MAIN":
            return self._main
        elif type is "TWITTER":
            return self._twitterApp
        elif type is "AWS":
            return self._aws
        elif type is "DB":
            return self._db
        else:
            raise SystemError("Type %s is not supported" % type)

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
