#!/bin/bash -eux

apt-get -qq update
apt-get -y -qq upgrade
apt-get -y -qq install software-properties-common
apt-get -y -qq install apt-utils

apt-add-repository ppa:ansible/ansible
apt-get -qq update
apt-get -y -qq install ansible
