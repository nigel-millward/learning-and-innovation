#!/bin/sh

# This does not work - Docker has limitation where you cant pass env variables into a running container with docker exec
# Instead, you must stop the container, add the env exports, and then restart the container
# aws_credentials_startup_script.sh can be used to automate populating new credentials in repo sdp-mwaa-local-runner


# GET AWS CREDENTIALS
AWS_ACCOUNT_ID=442494022606
PATH_TO_PEM="/Users/millwn04/Documents/certs/nmillwn04.pem"

response=$(curl -s "https://wormhole.api.bbci.co.uk/account/$AWS_ACCOUNT_ID/credentials" \
      --cert "$PATH_TO_PEM" \
      --cert-type PEM)

AWS_ACCESS_KEY_ID=$(jq -r '.accessKeyId' <<< ${response})
AWS_SECRET_ACCESS_KEY=$(jq -r '.secretAccessKey' <<< ${response})
AWS_SESSION_TOKEN=$(jq -r '.sessionToken' <<< ${response})


# EXPORT AWS CREDENTIALS IN DOCKER CONTAINER
container_name="aws-mwaa-local-runner-2_9-local-runner-1"

if [  "$(docker ps -a -q -f name=$container_name)" ]; then
  echo "Docker $container_name is running"
  
  docker exec -i $container_name  /bin/bash -c "export VAR1=VAL1 && export VAR2=VAL2"
  
  export AWS_DEFAULT_REGION='eu-west-1'
  export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
  export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
  export AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN

  echo "Airflow AWS exports:"
  export -p | grep -e '^export AWS_'
fi