# roger-monitoring

This repo contains everything you need to set up a monitoring system that can be used to monitor [roger-mesos](https://github.com/seomoz/roger-mesos) and tasks running on it.

### Setting up Influxdb
* To install influxdb use the following example:
  ```
  ansible-playbook -i ../../roger-mesos/vagrant/single_node/hosts/single monitoring-backend.yml -e @$HOME/rogeros-ansible-secrets.yml.encrypted --vault-password-file ~/.rogeros-ansible-vault-pass --diff --skip-tags="influx_backup,create_influx_databases,retention_policy,influx_users,statsd-fe-influxdb,statsd-repeater"
  ```
* Note: The above command will skip creation of influx dbs or users, applying retetion policies and continuous queries and installing Telegraf or statsd-repeaters. Ideally, you won't want to run these tasks anytime you do an upgrade or restart influxdb. In case you do, given below are the commands. Run them in order.
* Create admin and other users for alertd and Grafana.Example:
  ``` 
  ansible-playbook -i ../../roger-mesos/vagrant/single_node/hosts/single monitoring-backend.yml -e @$HOME/rogeros-ansible-secrets.yml.encrypted --vault-password-file ~/.rogeros-ansible-vault-pass --diff --tags="influx_users" -e "create_db_users_grant_permissions=true"
  ```
* Create Influx databases for Statsd metrics.Example: 
  ```
   ansible-playbook -i ../../roger-mesos/vagrant/single_node/hosts/single monitoring-backend.yml -e @$HOME/rogeros-ansible-secrets.yml.encrypted --vault-password-file ~/.rogeros-ansible-vault-pass --diff --tags="create_influx_databases"
  ```
* Applying retention policies and Continuous queries. Example:
  ``` 
  ansible-playbook -i ../../roger-mesos/vagrant/single_node/hosts/single monitoring-backend.yml -e @$HOME/rogeros-ansible-secrets.yml.encrypted --vault-password-file ~/.rogeros-ansible-vault-pass --diff --tags="retention_policy" -e "apply_retentions_and_cqs=true" -e '{"databases": ["db1", "db2"]}'
  ```
** Note: The previous command just applies retention policies to all the databases passed by extra vars. To apply continuous queries on the Statsd databases, also add ```-e downsample_statsd_metrics=true``` to the command. To apply continuous queries on the Collectd database, also add ```-e downsample_collectd_metrics=true``` to the command.
* Dropping retention policies and Continuous queries. Example:
  ```
  ansible-playbook -i ../../roger-mesos/vagrant/single_node/hosts/single monitoring-backend.yml -e @$HOME/rogeros-ansible-secrets.yml.encrypted --vault-password-file ~/.rogeros-ansible-vault-pass --diff --tags="drop_retention_policy" -e "drop_retentions_and_cqs=true" -e '{"databases": ["db1", "db2"]}'
  ```
* Running backup for your databases. Note: This assumes you have setup a snitch url(s) for your host(s) and put them in the ansible secrets file.
Example:
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
