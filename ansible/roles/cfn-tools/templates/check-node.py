#!/usr/bin/env python

import boto3
import importlib
import logging
import requests
import os
import sys
import subprocess

from os.path import basename


def get_stack_name(instance, region):
    ec2 = boto3.resource('ec2', region)
    ec2instance = ec2.Instance(instance)
    stack_name = ''
    for tags in ec2instance.tags:
        if tags['Key'] == 'aws:cloudformation:stack-name':
            stack_name = tags['Value']
    return stack_name


def main():
    log_level = os.getenv('CHECKS_LOG_LEVEL', 'INFO')
    logging.basicConfig(level=logging.getLevelName(log_level), format='%(levelname)s | %(message)s')

    aws_region = requests.get('http://169.254.169.254/latest/dynamic/instance-identity/document').json().get('region')
    instance_id = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text
    stack_name = get_stack_name(instance_id, aws_region)

    logging.debug('AWS Region: {}'.format(aws_region))
    logging.debug('Instance ID: {}'.format(instance_id))
    logging.debug('Stack Name: {}'.format(stack_name))

    checks_directory = os.getenv('CHECKS_DIR', '/opt/check/checks.d')
    sys.path.append(checks_directory)

    logging.info('=================== Begin Checks ===================')

    check_files = sorted(os.listdir(checks_directory))
    checked_run = False

    for filename in check_files:
        if filename.endswith("-check.py"):
            checked_run = True
            check_file = os.path.splitext(basename(filename))[0]

            logging.info('Running {} ---'.format(check_file))
            Check = getattr(importlib.import_module(check_file), 'Check')
            check = Check()
            try:
                check.run()
            except Exception, e:
                logging.error(' * Check {} failed: {}'.format(check_file, str(e)))
                signal_cf_stack(stack_name, aws_region, 'false', str(e))
                exit(1)

    if not checked_run:
        logging.warn('No check files found in {}...'.format(checks_directory))

    logging.info('=================== Finish Checks ==================')

    # ----------------------------------------------
    #    Tests all passed if we get to this point
    # ----------------------------------------------
    signal_cf_stack(stack_name, aws_region, 'true')


def signal_cf_stack(stack_name, aws_region, success_bool, fail_reason = 'none'):
    logging.info('Signalling ---')
    logging.info(' * stack = {}'.format(stack_name))
    logging.info(' * region = {}'.format(aws_region))
    logging.info(' * success = {}'.format(success_bool))

    if success_bool != 'true':
        logging.info(' * fail_reason = {}'.format(fail_reason))

    command = '/usr/local/bin/cfn-signal --stack {} --resource asg --region {} --success {} --reason "{}"'.format(stack_name, aws_region, success_bool, fail_reason)

    process = None
    with open(os.devnull, 'w') as quiet:
        process = subprocess.Popen(command, shell=True, stdout=quiet, stderr=quiet)
    process.wait()


if __name__ == '__main__':
    main()
