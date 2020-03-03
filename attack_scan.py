#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess
import datetime
import getpass
import re

try:
    import nmap
except ModuleNotFoundError:

    print("Python-nmap module not found")
    install_choice = input("Would you like to install python-nmap? Y/N\n")
    if install_choice.lower() == "y" or install_choice.lower == "yes":
        try:
            os.system("pip3 install python-nmap")
        except:

            print("Could not install python-nmap module")
            exit(-1)
        print("\npython-nmap module installed successfully\nRunning original command")
        cmdstr = ""
        for arg in sys.argv:
            cmdstr += arg + " "
        os.system(cmdstr)
        exit(0)

    else:
        print("Python-nmap will not be installed")
        exit(0)


def main():
    ports = ""
    hosts = ""
    print_check = False
    command = ""
    log = ""

    parser = argparse.ArgumentParser(
        description="attack_scan is a combination network scanner and attack automator. "
        "It can be used to automate network attacks or vulnerability tests "
        "across multiple hosts and ports using nmap to scan and user given "
        "command to execute across the found network."
    )

    parser.add_argument(
        "-cmd",
        metavar="-command",
        type=str,
        help="Full command in quotes for attack_scan to run on open found IP addresses, replace the IP address"
        " in the command to be automated with HOST and port with PORT "
        ' Example: -cmd "nikto -Tuning 89 -host HOST -p PORT"'
        "",
    )
    parser.add_argument("-print", action="store_true", help="Prints the scan")
    parser.add_argument(
        "-p",
        metavar="-port",
        type=str,
        help="Set ports to scan, default is top 1000 ports",
    )
    parser.add_argument(
        "-t", metavar="-target", type=str, help="Target IP address or range"
    )
    parser.add_argument(
        "-log",
        type=str,
        help="Directory to send logs to, if unspecified goes to "
        "/root/attack_scan_logs or if non root /home/user/attack_scan_logs",
    )
    if not len(sys.argv[1:]):
        parser.print_help()
        exit(0)
    try:
        args = parser.parse_args()
        if args.p:
            ports = args.p
        if args.t:
            hosts = args.t
        if args.print:
            print_check = args.print
        if args.cmd:
            command = str(args.cmd)
        if args.log:
            log = args.log

    except argparse.ArgumentError as e:
        print(e)
        parser.print_usage()

    print("Scanning...")
    nm = scan(str(ports), str(hosts))
    print("Scan complete")
    if print_check:
        print_scan(nm)
    else:
        if input("Would you like to print scan results? Y/N").lower() == "y":
            print_scan(nm)
    if input("Ready to attack? Y/N\n").lower() == "y":
        do_attack(nm, str(command), str(log))
    else:
        print("Not ready to attack, terminating program")
        exit(0)


def scan(ports, hosts):
    nm = nmap.PortScanner()
    if ports == "":
        nm.scan(hosts=hosts)
    else:
        nm.scan(ports=ports, hosts=hosts)
    return nm


def print_scan(nm):
    for host in nm.all_hosts():
        print("-------------------------------")
        print("Host : %s (%s)" % (host, nm[host].hostname()))
        print("State : %s" % nm[host].state())

        for protocol in nm[host].all_protocols():
            print("---------------")
            print("Protocol : %s" % protocol)
            port_state = nm[host][protocol].keys()

            for port in port_state:
                print(
                    "port : %s\tstate : %s" % (port, nm[host][protocol][port]["state"])
                )


def do_attack(nm, command, log):
    base_command = command
    if log:
        out = create_log(log)
    else:
        user = getpass.getuser()
        if user == "root":
            path = "/root/attack_scan_logs"
        else:
            path = "/home/" + user + "/attack_scan_logs"
        if not os.path.isdir(path):
            os.makedirs(path)
        out = create_log(path)
    print("Sending logs to", path)
    print("Performing the following attacks:\n")
    for host in nm.all_hosts():
        for protocol in nm[host].all_protocols():
            for port in nm[host][protocol].keys():
                command = re.sub("HOST", host, base_command)
                command = re.sub("PORT", str(port), command)
                print(command)

                subprocess.Popen(command, stdout=out, shell=True).wait()
    out.close()
    print("\nAttack complete")


def create_log(log):
    if os.path.isdir(log):
        log_dir = log
        now = datetime.datetime.now()
        out = open(
            log_dir + "/atk_out" + now.strftime("%Y-%m-%d--%H-%M-%S") + ".log", "a"
        )
        out.write("STDOUT FILE FOR " + now.strftime("%Y-%m-%d--%H-%M-%S") + " ATTACK")
        out.flush()
        return out


if __name__ == "__main__":
    main()
