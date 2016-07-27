# roger-monitoring

This repo contains everything you need to set up a monitoring system that can be used to monitor [roger-mesos](https://github.com/seomoz/roger-mesos) and tasks running on it.

### Influxdb Restore
* The influxdb role is set up to do incremental backups of the databases.
* To do a restore of a database, here is an example:
  ``` influxd restore -metadir <meta_dir_to_restore> -datadir <data_dir_to_restore> -database <database> <backup_dir>  ```

### Retention policies and Continuous queries
* When applying retention policies and continuous queries the databases, you need to specify the list of "databases" on which to apply them. Example:
  ```
    ansible-playbook -i ../../roger/ansible/hosts/influx monitoring-backend.yml -e @$HOME/rogeros-ansible-secrets.yml.encrypted --vault-password-file ~/.rogeros-ansible-vault-pass --diff --tags="retention_policy" -e "apply_retentions_and_cqs=true" --check -e '{"databases": ["db1", "db2"]}'
  ```  
* Same applies when you want to drop retention policies and continuous queries for a list of databases. Use the '-e "apply_retentions_and_cqs=true"' with your command.

#### Note
* We are using git submodules in this repo. So, when cloning this repo ensure that you fetch submodules. Here's how:
  * When cloning a repo for the first time (for git version > 1.6.5):
  ```
  $ git clone --recursive git@github.com:seomoz/roger-monitoring.git
  ```
  * On an existing cloned repo (or older version of git)
  ```
  $ cd roger-monitoring
  $ git submodule update --init --recursive
  ```
