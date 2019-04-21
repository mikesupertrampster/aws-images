#!/bin/bash -eux

apt-get update
apt-get  -y install apt-utils software-properties-common

apt-add-repository ppa:ansible/ansible
apt-get update
apt-get -y install ansible
