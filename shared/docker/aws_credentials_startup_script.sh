# GET AWS CREDENTIALS
AWS_ACCOUNT_ID=442494022606
PATH_TO_PEM="/Users/millwn04/Documents/certs/nmillwn04.pem"

response=$(curl -s "https://wormhole.api.bbci.co.uk/account/$AWS_ACCOUNT_ID/credentials" \
      --cert "$PATH_TO_PEM" \
      --cert-type PEM)

export AWS_DEFAULT_REGION='eu-west-1'
export AWS_ACCESS_KEY_ID=$(jq -r '.accessKeyId' <<< ${response})
export AWS_SECRET_ACCESS_KEY=$(jq -r '.secretAccessKey' <<< ${response})
export AWS_SESSION_TOKEN=$(jq -r '.sessionToken' <<< ${response})

export -p | grep -e '^export AWS_'