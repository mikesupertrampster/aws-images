#!/bin/bash

: "${AWS_STS_IAM_QUERY_ROLE_ARN:?AWS_STS_IAM_QUERY_ROLE_ARN not set}"

result=$(aws sts assume-role --role-arn "${AWS_STS_IAM_QUERY_ROLE_ARN}" --role-session-name "import_users")
export AWS_ACCESS_KEY_ID=$(echo "${result}" | jq --raw-output '.Credentials.AccessKeyId')
export AWS_SESSION_TOKEN=$(echo "${result}" | jq --raw-output '.Credentials.SessionToken')
export AWS_SECRET_ACCESS_KEY=$(echo "${result}" | jq --raw-output '.Credentials.SecretAccessKey')

aws iam get-group --group-name admin-group --query "Users[].[UserName]" --output text |

while read -r awsUsers; do
  username=$(echo "${awsUsers}" | cut -d'@' -f 1)

  if id -u "${username}" >/dev/null 2>&1; then
    echo "${username} exists"
  else
    echo "Creating user ${username}."
    sudofile=$(echo "${username}" | tr "." " ")

    /usr/sbin/adduser --firstuid 2000 --disabled-password --force-badname --gecos "" "${username}"
    echo "${username} ALL=(ALL) NOPASSWD:ALL" > "/etc/sudoers.d/${sudofile}"
  fi
done