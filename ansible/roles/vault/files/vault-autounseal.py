#!/usr/bin/env python

import boto3
import base64
import hvac
import logging
import requests
import os
import sys

from retry import retry
from requests.packages.urllib3.exceptions import InsecureRequestWarning


@retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
def initialise_vault(vault, table, key_id, kms):
    logging.info('initialise_vault()')

    keys = vault.sys.initialize(secret_shares=2, secret_threshold=2, pgp_keys=None)
    for key in keys['keys']:
        result = kms.encrypt(KeyId=key_id, Plaintext=key)
        binary_encrypted = result[u'CiphertextBlob']
        encrypted_key = base64.b64encode(binary_encrypted)
        table.put_item(
            Item={'key': encrypted_key}
        )


@retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
def unseal(vault, table, kms):
    logging.info('unseal()')
    keys = table.scan()
    for encrypted_key in keys['Items']:
        binary_data = base64.b64decode(encrypted_key['key'])
        meta = kms.decrypt(CiphertextBlob=binary_data)
        key = meta[u'Plaintext']
        vault.sys.submit_unseal_key(key)


@retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
def is_initialised(vault):
    return vault.sys.is_initialized()


@retry(tries=5, delay=5, max_delay=120, backoff=2, jitter=0)
def is_sealed(vault):
    return vault.sys.is_sealed()


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    log_level = os.getenv('VAULT_AUTOUNSEAL_LOG_LEVEL', 'INFO')
    vault_addr = os.getenv('VAULT_ADDR', 'https://localhost:8200')
    vault_unseal_kms = os.getenv('VAULT_UNSEAL_KEY_ID')
    vault_unseal_dynamodb = os.getenv('VAULT_UNSEAL_DYNAMODB_TABLE')

    logging.basicConfig(level=logging.getLevelName(log_level), format='%(levelname)s | %(message)s')
    vault = hvac.Client(url=vault_addr, verify=False)

    if not vault_unseal_kms:
        logging.error('VAULT_UNSEAL_KEY_ID not defined')
        sys.exit(1)

    if not vault_unseal_dynamodb:
        logging.error('VAULT_UNSEAL_DYNAMODB_TABLE not defined')
        sys.exit(1)

    session = boto3.session.Session()
    kms = session.client('kms')
    key_id = vault_unseal_kms

    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(vault_unseal_dynamodb)

    if not is_initialised(vault):
        initialise_vault(vault, table, key_id, kms)
    else:
        logging.info('Vault already initialised.')

    if is_sealed(vault):
        unseal(vault, table, kms)
    else:
        logging.info('Vault already unsealed.')


if __name__ == '__main__':
    main()
