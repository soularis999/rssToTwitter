import logging
import boto3
import os
import sys

from process_rss import process
from base64 import b64decode
from feed_config import APP_TWITTER_KEY_ENV, APP_TWITTER_SECRET_ENV, USER_TWITTER_KEY_ENV, USER_TWITTER_SECRET_ENV, \
    AWS_KEY_ENV, AWS_SECRET_ENV


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

    # try:
    #     os.environ[APP_TWITTER_KEY_ENV] = \
    #         boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ[APP_TWITTER_KEY_ENV]))['Plaintext']
    # except TypeError:
    #     pass

    # try:
    #     os.environ[APP_TWITTER_SECRET_ENV] = \
    #         boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ[APP_TWITTER_SECRET_ENV]))['Plaintext']
    # except TypeError:
    #     pass

    # try:
    #     os.environ[USER_TWITTER_KEY_ENV] = \
    #         boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ[USER_TWITTER_KEY_ENV]))['Plaintext']
    # except TypeError:
    #     pass

    # try:
    #     os.environ[USER_TWITTER_SECRET_ENV] = \
    #         boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ[USER_TWITTER_SECRET_ENV]))['Plaintext']
    # except TypeError:
    #     pass

    # if AWS_KEY_ENV in os.environ and AWS_SECRET_ENV in os.environ:
    #     try:
    #         os.environ[AWS_KEY_ENV] = \
    #             boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ[AWS_KEY_ENV]))['Plaintext']
    #     except TypeError:
    #         pass

    #     try:
    #         os.environ[AWS_SECRET_ENV] = \
    #             boto3.client('kms').decrypt(CiphertextBlob=b64decode(os.environ[AWS_SECRET_ENV]))['Plaintext']
    #     except TypeError:
    #         pass

    return process(dry_run, is_aws, *files)
