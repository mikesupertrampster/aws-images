#!/usr/bin/env python

import sys
import semver
import subprocess


def git(*args):
    return subprocess.check_output(['git'] + list(args))


def tag_repo(tag):
    git('tag', '-a', tag, '-m', '"Version created by gen-semver."')
    git('push', 'origin', tag)


def bump(latest):
    return semver.bump_patch(latest)


def main():
    try:
        latest = git('describe', '--tags').decode().strip()
    except subprocess.CalledProcessError:
        version = '1.0.0'
    else:
        version = bump(latest)

    # tag_repo(version)
    print(version)
    return 0


if __name__ == '__main__':
    sys.exit(main())
