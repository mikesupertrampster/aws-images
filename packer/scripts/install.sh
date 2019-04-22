#!/bin/bash -eux

apt-get update -q
apt-get install -y -q apt-utils
apt-get upgrade -y -q
sleep 5; apt-get install -y -q software-properties-common

apt-add-repository ppa:ansible/ansible
apt-get update -y -q
apt-get install -y -q ansible
