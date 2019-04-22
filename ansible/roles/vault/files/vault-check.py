#!/usr/bin/env python

from base import BaseCheck


class Check(BaseCheck):

    def check(self, **kwargs):
        self.systemd_unit_is_running('vault.service')

        vault_tcp_ports = [8200, 8201]
        self.ports_is_being_listened(vault_tcp_ports)

        self.vault_initialised('https://localhost:8200')