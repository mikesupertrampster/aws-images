#!/usr/bin/env bash

match_pattern="${1}"
git_range=${2:-"HEAD HEAD~1"}
changes=$(git diff --name-only ${git_range})
changed="false"

if [[ ${changes} =~ "${match_pattern}" ]]; then
    changed="true"
fi

echo ${changed}