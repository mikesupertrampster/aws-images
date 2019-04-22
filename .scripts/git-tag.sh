#!/usr/bin/env bash

mkdir -p ~/.ssh && echo "${GITHUB_DEPLOY_KEY}" > ~/.ssh/id_rsa && chmod 200  ~/.ssh/id_rsa
echo -e "Host *\n    StrictHostKeyChecking no" > ~/.ssh/config

git remote set-url origin ${GITHUB_SSH_URL}
git config --global user.email "Gitlab CI"
git config --global user.name "Gitlab CI"

.scripts/gen-semver.py > semver