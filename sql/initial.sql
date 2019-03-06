create table store(v_name varchar(128) not null primary key, v_last_id varchar(4000), t_stamp bigint);

create table store_audit(v_name varchar(128) not null, v_last_id varchar(4000), t_stamp bigint, update_ts timestamp);

CREATE OR REPLACE FUNCTION log_store()
  RETURNS trigger AS
$$
BEGIN
  INSERT INTO store_audit (v_name, v_last_id, t_stamp, update_ts)
  VALUES(OLD.v_name, OLD.v_last_id, OLD.t_stamp, now());
  RETURN NEW;
END;
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER store_log_trigger
  AFTER UPDATE ON store
  FOR EACH ROW
  EXECUTE PROCEDURE log_store();
