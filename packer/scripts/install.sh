#!/bin/bash -eux

apt-get -qq update -qq
apt-get -y -qq install -qq apt-utils
apt-get -y -qq upgrade -qq
sleep 5; apt-get -y -qq install -qq software-properties-common

apt-add-repository ppa:ansible/ansible
apt-get -qq update -qq
apt-get -y -qq install -qq ansible
