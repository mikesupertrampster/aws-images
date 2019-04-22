#!/usr/bin/env bash

source /etc/environment
if [[ -z "${1}" ]]; then exit 1; fi

result=$(aws sts assume-role --role-arn "${AWS_STS_IAM_QUERY_ROLE_ARN}" --role-session-name "import_users")
export AWS_ACCESS_KEY_ID=$(echo "${result}" | jq --raw-output '.Credentials.AccessKeyId')
export AWS_SESSION_TOKEN=$(echo "${result}" | jq --raw-output '.Credentials.SessionToken')
export AWS_SECRET_ACCESS_KEY=$(echo "${result}" | jq --raw-output '.Credentials.SecretAccessKey')

aws iam list-ssh-public-keys --user-name "${1}" --query "SSHPublicKeys[?Status == 'Active'].[SSHPublicKeyId]" --output text |

while read -r sshkey; do
  aws iam get-ssh-public-key --user-name "${1}" --ssh-public-key-id "${sshkey}" --encoding SSH --query "SSHPublicKey.SSHPublicKeyBody" --output text
done
