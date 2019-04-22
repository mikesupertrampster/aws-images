#!/bin/bash -eux

apt-get update
apt-get -y upgrade
apt-get -y install software-properties-common
apt-get -y install apt-utils

apt-add-repository ppa:ansible/ansible
apt-get update
apt-get -y install ansible
