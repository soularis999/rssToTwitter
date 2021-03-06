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
        section = util.encode(section)
        return self._stores[section] if section in self._stores else None

    def __len__(self):
        """
        returns the number of configured services
        :return:
        """
        return len(self._stores)

    def __str__(self):
        return self._stores.__str__()


class FileBasedDataStore(DataStore):
    def __init__(self, config, dry_run=False):
        DataStore.__init__(self, dry_run)
        self._config = config
        self._read_store()

    def _read_store(self):
        """
        Read the last updated records from store
        :return dict of store objects indexed by service name
        """
        self._stores = {}
        f_path = os.path.expanduser(self._config.storeFileName)
        log.info("reading store %s" % f_path)

        if not os.path.exists(f_path):
            return

        with open(f_path, 'r') as f:
            for line in f:
                data = line.strip().split("|")
                section_name = util.encode(data[0])

                time = int(data[2]) if data[2] else None
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
        f_path = os.path.expanduser(self._config.storeFileName)
        log.info("writing store %s" % f_path)

        def write(service_name, store):
            post_id = store.lastProcessedId if store.lastProcessedId else ''
            time = '%i' % store.lastProcessedUpdateTimestamp if store.lastProcessedUpdateTimestamp else ''
            text = '%s|%s|%s\n' % (service_name, post_id, time)
            return text

        # write everything in store
        results = list(map(lambda sname: write(sname, self._stores[sname]), self._stores.keys()))
        if not self._dry_run:
            with open(f_path, 'w') as f:
                f.writelines(results)

        log.info("Saved %i records" % len(results))
        if result_text is not None:
            result_text.append(results)
        return len(results)


class S3BasedDataStore(FileBasedDataStore):
    def __init__(self, config, aws_config, dry_run=False):
        self._aws_config = aws_config
        self._aws_file_name = self._aws_config.awsFileName

        from boto3 import resource

        self._connection = resource('s3') \
            if not aws_config.awsAccessKey or not aws_config.awsAccessSecret \
            else resource('s3', aws_access_key_id=aws_config.awsAccessKey,
                          aws_secret_access_key=aws_config.awsAccessSecret)
        log.debug("s3 connection opened")

        self._connection.Bucket(aws_config.awsBucket).download_file(self._aws_file_name, config.storeFileName)
        log.debug("%s file copied from s3" % config.storeFileName)

        FileBasedDataStore.__init__(self, config, dry_run=dry_run)

    def write_store(self, result_text=None):
        super(S3BasedDataStore, self).write_store(result_text=result_text)
        if not self._dry_run:
            self._connection.Bucket(self._aws_config.awsBucket).upload_file(self._config.storeFileName,
                                                                            self._aws_file_name)

            
class DBBasedDataStore(DataStore):
    def __init__(self, config, dry_run=False):
        DataStore.__init__(self, dry_run)
        self._config = config
        self._read_store()    

    def _read_store(self):
        """
        Read the last updated records from store
        :return dict of store objects indexed by service name
        """
        self._stores = {}
        log.info("reading db store")
        conn = self._get_connection()
        with conn.cursor() as curs:

            curs.execute("select v_name, v_last_id, t_stamp from store")
            data = curs.fetchone()
            
            while data is not None:
                section_name = util.encode(data[0])
                last_id = data[1]
                time = data[2]
                if last_id and time: 
                    record = STORE(section_name, data[1], time)
                    log.debug("processing store record %s" % (record,))
                    self._stores[section_name] = record
                else:
                    log.error("Could not parse the record for %s" % data)
                    self._stores[section_name] = None
                    
                data = curs.fetchone()
                
        conn.close()

    def write_store(self, result_text=None):
        """
        After the services were updated with latest information the writeStore has to be called to persists the
        data into the file. The file will be read on startup
        :param result_text the list item that will be populated with text writen to db
        :return: number of items written
        """        
        def collect(service_name, store):
            post_id = store.lastProcessedId if store.lastProcessedId else None
            time = int(store.lastProcessedUpdateTimestamp) if store.lastProcessedUpdateTimestamp else -1
            return (post_id, time, service_name)

        results = list(map(lambda sname: collect(sname, self._stores[sname]), self._stores.keys()))
        print(results)
        
        log.info("writing db store")
        
        conn = self._get_connection()
        with conn.cursor() as curs:
            curs.execute("select v_name from store")
            existing_names = list(map(lambda rec: rec[0], curs.fetchall()))
            log.info("Existing: %s" % ",".join(existing_names))
            
            for record in results:
                query = 'update store set v_last_id=%s, t_stamp=%s where v_name=%s' if record[2] in existing_names else \
                    'insert into store (v_last_id, t_stamp, v_name) values (%s, %s, %s)'
                log.info("Query %s, %s", query, record)
                if not self._dry_run:
                    curs.execute(query, record)
            conn.commit()
        conn.close()
                
        log.info("Saved %i records" % len(results))
        if result_text is not None:
            result_text.append(results)
        return len(results)

    def clean_audit_log(self, days):
        """
        Function is purposely built for cleaning up the logs written to audit table
        :param days How many days back to go to delete the records
        :return None
        """
        conn = self._get_connection()
        with conn.cursor() as curs:
            query = "delete from store_audit where update_ts < now() - interval '%s days'"
            log.info("Delete audit records %s" % (query % days))
            if not self._dry_run:
                curs.execute(query, (days,))
                conn.commit()
        conn.close()
        
    def _get_connection(self):
        import psycopg2
        if self._config.sslmode:
            return psycopg2.connect(self._config.url, sslmode=self._config.sslmode)
        else:
            return psycopg2.connect(self._config.url)            

