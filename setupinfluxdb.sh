#!/bin/bash

TIME_NOW=$(date)

if [ $# -lt 2 ]; then
    echo "Usage: setupinfluxdb.sh <roger-monitoring repo dir> <databases>"
    echo 'Example: bash setupinfluxdb.sh ./ "db1 db2 db3"'
    exit 1
fi

REPO_DIR="$1"
DATABASES="$2"
ARR_DATABASES=( $DATABASES )

databases="[ \"{{ tools_database }}\","
for ((i=0; i<(${#ARR_DATABASES[*]}-1); i++));
do
    databases="$databases \"${ARR_DATABASES[i]}\","
done
last_element=${ARR_DATABASES[${#ARR_DATABASES[@]} - 1]}
databases="$databases \"$last_element\"]"

echo "*** Setting up Influxdb on your Single node local cluster at $TIME_NOW ***"

echo "Installing influxdb..."

ansible-playbook -i $REPO_DIR/../roger-mesos/vagrant/single_node/hosts/single $REPO_DIR/ansible/monitoring-backend.yml -e "@$REPO_DIR/ansible_vars.yml" --diff --skip-tags="influx_backup,create_influx_databases,retention_policy,influx_users,statsd-fe-influxdb,statsd-repeater" --user=vagrant --ask-pass

echo "Creating influxdb users and granting privileges"

ansible-playbook -i $REPO_DIR/../roger-mesos/vagrant/single_node/hosts/single $REPO_DIR/ansible/monitoring-backend.yml -e "@$REPO_DIR/ansible_vars.yml" --diff --tags="influx_users" --user=vagrant --ask-pass -e "create_db_users_grant_permissions=true" -e "{\"statsd_databases\": $databases }"

echo "Creating databases"

ansible-playbook -i $REPO_DIR/../roger-mesos/vagrant/single_node/hosts/single $REPO_DIR/ansible/monitoring-backend.yml -e "@$REPO_DIR/ansible_vars.yml" --diff --tags="create_influx_databases" --user=vagrant --ask-pass -e "{\"databases_to_backup\": \"$DATABASES {{ tools_database }}\"}"

echo "Applying Retention policies on databases"

ansible-playbook -i $REPO_DIR/../roger-mesos/vagrant/single_node/hosts/single $REPO_DIR/ansible/monitoring-backend.yml -e "@$REPO_DIR/ansible_vars.yml" --diff --tags="retention_policy" --user=vagrant --ask-pass -e "apply_retentions_and_cqs=true" -e "{\"databases\": $databases }"

echo "Installing and setting up Telegraf for Statsd metrics"

ansible-playbook -i $REPO_DIR/../roger-mesos/vagrant/single_node/hosts/single $REPO_DIR/ansible/monitoring-backend.yml -e "@$REPO_DIR/ansible_vars.yml" --diff --tags="statsd-fe-influxdb" --user=vagrant --ask-pass
