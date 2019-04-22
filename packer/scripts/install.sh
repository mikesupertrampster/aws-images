#!/bin/bash -eux

apt-get -qq update
apt-get -y -qq install apt-utils
apt-get -y -qq upgrade
sleep 5; apt-get -y -qq install software-properties-common

apt-add-repository ppa:ansible/ansible
apt-get -qq update
apt-get -y -qq install ansible
