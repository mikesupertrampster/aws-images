#!/bin/bash -eux

apt-get update -qq
apt-get install -y -qq apt-utils
apt-get upgrade -y -qq
sleep 5; apt-get install -y -qq software-properties-common

apt-add-repository ppa:ansible/ansible
apt-get update -y -qq
apt-get install -y -qq ansible
