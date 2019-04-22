#!/usr/bin/env python

from base import BaseCheck


class Check(BaseCheck):

    def check(self, **kwargs):
        self.systemd_unit_is_running('import-users.timer')
        self.user_exists(2000)
