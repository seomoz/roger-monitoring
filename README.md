# roger-monitoring

This repo contains everything you need to set up a monitoring system that can be used to monitor [roger-mesos](https://github.com/seomoz/roger-mesos) and tasks running on it.

### Setting up Influxdb
* To install influxdb use the following script (Installs influxdb, creates users and privileges, creates databases and applies retention policies).
* Usage: setupinfluxdb.sh <roger-monitoring repo dir> <databases>. Example usage: 
  ```
  bash roles/monitoring-influxdb/files/setupinfluxdb.sh ./ 'db1 db2 db3'  
  ```

* Note: To apply continuous queries on the Statsd databases, also add ```-e downsample_statsd_metrics=true``` to the above command or to apply continuous queries on the collectd db add ```-e downsample_collectd_metrics=true``` to the above command.
 
#### Dropping retention policies and Continuous queries. 
* Example:
  ```
  ansible-playbook -i ../../roger-mesos/vagrant/single_node/hosts/single monitoring-backend.yml -e @$HOME/rogeros-ansible-secrets.yml.encrypted --vault-password-file ~/.rogeros-ansible-vault-pass --diff --tags="drop_retention_policy" -e "drop_retentions_and_cqs=true" -e '{"databases": ["db1", "db2"]}'
  ```

#### Running backup for your databases. Note: This assumes you have setup a snitch url(s) for your host(s) and put them in the ansible secrets file.
* Example:
  ```
  ansible-playbook -i ../../roger-mesos/vagrant/single_node/hosts/single monitoring-backend.yml -e @$HOME/rogeros-ansible-secrets.yml.encrypted --vault-password-file ~/.rogeros-ansible-vault-pass --diff --tags="influx_backup"
  ```

### Setting up Telegraf 
* To setup Telegraf on your machine, use the following example command:
  ```
  ansible-playbook -i ../../roger-mesos/vagrant/single_node/hosts/single monitoring-backend.yml -e @$HOME/rogeros-ansible-secrets.yml.encrypted --vault-password-file ~/.rogeros-ansible-vault-pass --diff --tags="statsd-fe-influxdb"
  ```

### Influxdb Restore
* The influxdb role is set up to do incremental backups of the databases.
* To do a restore of a database, here is an example:
  ``` influxd restore -metadir <meta_dir_to_restore> -datadir <data_dir_to_restore> -database <database> <backup_dir>  ```

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
