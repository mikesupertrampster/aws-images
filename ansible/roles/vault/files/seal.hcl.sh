#!/usr/bin/env bash
AWS_REGION=$(curl -s http://169.254.169.254/latest/dynamic/instance-identity/document | grep region | awk -F\" '{print $4}')

source /etc/environment

cat > "$1" << EOF
seal "awskms" {
  region     = "${AWS_REGION}"
  kms_key_id = "${VAULT_UNSEAL_KEY_ID}"
}
EOF