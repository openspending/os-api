#!/bin/bash
set -e

# This script is the entrypoint to the os-api Docker container. This will
# verify that the Elasticsearch and RabbitMQ environment variables are set and
# that Elasticsearch and RabbitMQ are running before executing the command
# provided to the docker container.

# Read parameters from the environment and validate them.
checkHost() {
    if [ -z "$$1" ]; then
        echo >&2 'Error: missing required $1 environment variable'
        echo >&2 '  Did you forget to -e $1=... ?'
        exit 1
    fi
}

readParams() {
  checkHost "OS_ELASTICSEARCH_ADDRESS"
  checkHost "OS_MQ_ADDRESS"
}

# Wait for elasticsearch to start. It requires that the status be either green
# or yellow.
waitForElasticsearch() {
  echo -n "Waiting on $1 to start."
  for ((i=1;i<=300;i++))
  do
    health=$(curl --silent "http://$1/_cat/health" | awk '{print $4}')
    if [[ "$health" == "green" ]] || [[ "$health" == "yellow" ]]
    then
      echo
      echo "Elasticsearch is ready!"
      return 0
    fi

    ((i++))
    echo -n '.'
    sleep 1
  done

  echo
  echo >&2 'Elasticsearch is not running or is not healthy.'
  echo >&2 "Address: ${OS_ELASTICSEARCH_ADDRESS}"
  echo >&2 "$health"
  exit 1
}

# Wait for RabbitMQ to start.
waitForRabbitMQ() {
  echo -n "Waiting for RabbitMQ to start."
  for ((i=1;i<=300;i++))
  do
    service=$(curl --silent "http://${OS_MQ_ADDRESS}:5672" | awk '{print $1}')
    if [[ "$service" = *"AMQP"* ]]
    then
      echo
      echo "RabbitMQ is ready!"
      return 0
    fi

    ((i++))
    echo -n '.'
    sleep 1
  done

  echo
  echo >&2 'RabbitMQ is not running or is not healthy.'
  echo >&2 "Address: ${OS_MQ_ADDRESS}:5672"
  echo >&2 "$service"
  exit 1
}

# Main
readParams
if [ ${OS_CHECK_ES_HEALTHY+x} ]
then
waitForElasticsearch $OS_ELASTICSEARCH_ADDRESS
fi
waitForRabbitMQ
exec "$@"
