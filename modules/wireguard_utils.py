#!/usr/bin/env python3
# modules/wireguard_utils.py
# Functions for working with WireGuard

import os
import subprocess

WIREGUARD_BINARY = "/usr/bin/wg"

def check_wireguard_installed():
    """Checks if WireGuard is installed."""
    return os.path.isfile(WIREGUARD_BINARY)
