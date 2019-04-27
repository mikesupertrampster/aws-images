#!/usr/bin/env bash
source /etc/environment

certbot certonly --agree-tos --non-interactive -d "${VAULT_FQDN}" \
                 --config-dir=/etc/vault/letsencrypt/config \
                 --work-dir=/etc/vault/letsencrypt/work \
                 --logs-dir=/etc/vault/letsencrypt/logs \
                 --dns-route53 -m ${CERT_RENEW_CONTACT_EMAIL:-abc@xyz.123} \
                 --server ${LETSENCRYPT_API}