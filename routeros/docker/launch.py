#!/usr/bin/env python3

import datetime
import logging
import os
import random
import re
import signal
import string
import sys
import telnetlib

import vrnetlab

def handle_SIGCHLD(signal, frame):
    os.waitpid(-1, os.WNOHANG)

def handle_SIGTERM(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, handle_SIGTERM)
signal.signal(signal.SIGTERM, handle_SIGTERM)
signal.signal(signal.SIGCHLD, handle_SIGCHLD)

TRACE_LEVEL_NUM = 9
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kws)
logging.Logger.trace = trace

class ROS_vm(vrnetlab.VM):
    def __init__(self, username, password):
        disk_image = None
        for e in sorted(os.listdir("/")):
            if not disk_image and re.search(".vmdk$", e):
                disk_image = "/" + e
        super(ROS_vm, self).__init__(username, password, disk_image=disk_image, ram=256)
        self.qemu_args.extend(["-boot", "n"])

        self.num_nics = 31
        
        if username == "admin":
            self.admin_password = password
        else:
            self.admin_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    def bootstrap_spin(self):
        if self.spins > 300:
            self.stop()
            self.start()
            return

        (ridx, match, res) = self.tn.expect([b"MikroTik Login"], 1)
        if match:
            if ridx == 0:
                self.logger.debug("VM started")

                self.wait_write("\r", None)
                self.wait_write("admin+ct", wait="MikroTik Login: ")
                self.wait_write("", wait="Password: ")
                self.wait_write("n", wait="Do you want to see the software license? [Y/n]: ")
                
                self.logger.debug("Handling password change prompt")
                self.logger.info("Setting admin password to: %s" % self.admin_password)
                self.wait_write(self.admin_password, wait="new password> ")
                self.wait_write(self.admin_password, wait="repeat new password> ")

                self.logger.debug("Login completed")

                self.bootstrap_config()
                self.tn.close()
                startup_time = datetime.datetime.now() - self.start_time
                self.logger.info("Startup complete in: %s" % startup_time)
                self.running = True
                return

        if res != b'':
            self.logger.trace("OUTPUT: %s" % res.decode())
            self.spins = 0

        self.spins += 1

        return

    def bootstrap_config(self):
        self.logger.info("applying bootstrap configuration")
        self.wait_write("/ip address add interface=ether1 address=10.0.0.15 netmask=255.255.255.0", "[admin@MikroTik] > ")

        if self.username != "admin":
            self.wait_write("/user add name=%s password=\"%s\" group=full" % (self.username, self.password), "[admin@MikroTik] > ")
            
        self.wait_write("\r", "[admin@MikroTik] > ")
        self.logger.info("completed bootstrap configuration")

class ROS(vrnetlab.VR):
    def __init__(self, username, password):
        super(ROS, self).__init__(username, password)
        self.vms = [ ROS_vm(username, password) ]

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--trace', default=vrnetlab.bool_from_env('TRACE'), action='store_true', help='enable trace level logging')
    parser.add_argument('--username', default=os.getenv('USERNAME', 'admin'), help='Username')
    parser.add_argument('--password', default=os.getenv('PASSWORD', 'admin'), help='Password')
    parser.add_argument('--hostname', default='vr-ros', help='Router hostname')
    parser.add_argument('--connection-mode', default='tc', help='Connection mode to use in the datapath')
    args = parser.parse_args()

    LOG_FORMAT = "%(asctime)s: %(module)-10s %(levelname)-8s %(message)s"
    logging.basicConfig(format=LOG_FORMAT)
    logger = logging.getLogger()

    logger.setLevel(logging.DEBUG)
    if args.trace:
        logger.setLevel(1)

    vr = ROS(args.username, args.password)
    vr.start()