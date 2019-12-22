from __future__ import print_function
from cloudmesh.shell.command import command
from cloudmesh.shell.command import PluginCommand
from cloudmesh.pi.api.manager import Manager
from cloudmesh.common.console import Console
from cloudmesh.common.util import path_expand
from cloudmesh.common.parameter import Parameter
# Couldn't get it working with Shell, had to use os.system() instead
#from cloudmesh.common.Shell import Shell
from cloudmesh.inventory.inventory import Inventory
from pprint import pprint
from cloudmesh.common.debug import VERBOSE
import os
import time

class PiCommand(PluginCommand):

    def get_host_ips(self, hosts, inv):
        """
        Given a list of hostnames and an inventory dict, return a list of IPs
          corresponding to the hostnames. Returns None in case of error.

        :param hosts: list of hostnames
        :param inv: dict from Inventory().read() => .list()
        """

        ips = []
        for host in hosts:
            if host not in inv.keys():
                print(f"No host {host} in inventory!")
                return None
            ip = inv[host]['ip']
            if ip == '':
                print(f"Host {host} has no IP in inventory!")
                return None
            ips.append(ip)
        return ips


    def run_many_commands(self, ips, commands):
        """
        :param ips: list of IPs
        :param commands: list of shell commands to run on every IP
        """

        template_begin = "for i in "
        template_end = "; do ssh $i {}; done"
        template_middle = ""
        for ip in ips:
            template_middle += f"pi@{ip} "
        sys_cmd = template_begin + template_middle + template_end

        # sys_cmd is now like:
        #   for i in pi@IP1 pi@IP2 pi@IP3; do ssh $i {}; done
        # the {} means it can be used with string.format() to run a command
        # if a command is an empty string, it will just launch a normal SSH session
        #   (since {} gets replaced with "" => ssh has no args aside from pi@IP)
        for command in commands:
            os.system(sys_cmd.format(command))


    # noinspection PyUnusedLocal
    @command
    def do_pi(self, args, arguments):
        """
        ::

          Usage:
                pi ssh HOSTS
                pi setup1 HOSTS
                pi setup2 HOSTS
                pi setupmaster HOSTS
                pi cmd HOSTS CMD

          Arguments:
              HOSTS   hostlist
              CMD     command

          Description:

              This command configures Pis for Kubernetes clusters.
              pi ssh HOSTS:
                  Launch an interactive SSH session on each host.
                  When you logout from one host, it will automatically SSH to
                    the next host in the list.

              pi setup1 HOSTS:
                  Run part 1 of Kubernetes setup on the hosts.

              pi setup2 HOSTS:
                  Run part 2 of Kubernetes setup on the hosts.

              pi setupmaster HOSTS:
                  Configure the HOSTS as Kubernetes masters.
                  HOSTS will probably just be one hostname here.

              pi cmd HOSTS CMD:
                  Run CMD on every host via SSH.
                  If CMD is more than one word it should be contained in quotes.
        """

        hosts = Parameter.expand(arguments.HOSTS)
        inv = Inventory()
        inv.read()
        inv = inv.list()
        ips = self.get_host_ips(hosts, inv)
        if ips == None: # error
            return ""

        if arguments.ssh:
            self.run_many_commands(ips, [''])
        elif arguments.setup1:
            self.setup_1(ips)
        elif arguments.setup2:
            self.setup_2(ips)
        elif arguments.setupmaster:
            self.setup_master(ips)

    def setup_1(self, ips):
        tz = 'America/Indiana/Indianapolis'
        print("$ timedatectl list-timezones    to list timezones")
        inp = input(f"Enter your timezone (blank for default {tz}): ")
        if inp != '':
            tz = inp

        commands = [
            "'sudo timedatectl set-ntp false'",
            f"'sudo timedatectl set-timezone {tz}'"
        ]

        # final command is like 'sudo timedatectl set-time "2019-12-18 14:20:52"'
        currtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        final_cmd = f"'sudo timedatectl set-time \"{currtime}\"'"
        commands.append(final_cmd)

        self.run_many_commands(ips, commands)

    def setup_2(self, ips):
        commands = [
            "'echo \"deb http://apt.kubernetes.io/ kubernetes-xenial main\" | sudo tee /etc/apt/sources.list.d/kubernetes.list'",
            "'sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 6A030B21BA07F4FB'",
            "'sudo apt-get update'",
            "'sudo apt-get -y dist-upgrade'",
            "'sudo apt-get -y install kubelet kubeadm kubectl'",
            "'sudo dphys-swapfile swapoff'",
            "'sudo dphys-swapfile uninstall'",
            "'sudo update-rc.d dphys-swapfile remove'",
            "'sudo apt -y purge dphys-swapfile'",
            "'sudo reboot'",
        ]

        self.run_many_commands(ips, commands)

    def setup_master(self, ips):
        commands = [
            "'sudo kubeadm init'",
            "'mkdir -p /home/pi/.kube'",
            "'sudo cp -i /etc/kubernetes/admin.conf /home/pi/.kube/config'",
            "'sudo chown 1000:1000 /home/pi/.kube/config'",
        ]

        self.run_many_commands(ips, commands)
