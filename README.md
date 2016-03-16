# roger-monitoring

This repo contains everything you need to set up a monitoring system that can be used to monitor [roger-mesos](https://github.com/seomoz/roger-mesos) and tasks running on it.

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
