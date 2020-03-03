#!/usr/bin/env python3
import sys
import os
import argparse
import subprocess
import datetime
import getpass

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
    prnt = False
    command = ""
    log = ""

    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        "-cmd",
        metavar="-command",
        type=str,
        help="Full command in quotes for attack_scan to run on open found IP addresses"
        ' Example: -cmd "nikto -tuning 89 -host "'
        "",
    )
    parser.add_argument("-print", action="store_true", help="Prints the scan")
    parser.add_argument(
        "-p",
        metavar="-port",
        # nargs="+",
        type=str,
        help="Set ports, can use range Example -p 22-443 default is top 1000 ports, if port is found, will "
             "send attack to that port",
    )
    parser.add_argument(
        "-t",
        metavar="-target",
        type=str,
        help="Target IP address or range",
    )
    parser.add_argument(
        "-log", metavar="-log", type=str, help="Directory to send logs to"
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
            prnt = args.print
        if args.cmd:
            command = str(args.cmd)
        if args.log:
            log = args.log

    except Exception as e:
        print(e)

    print("Scanning...")
    nm = scan(str(ports), str(hosts))
    ready = input("Ready to attack? Y/N\n")
    if ready.lower() == "y" or ready.lower() == "yes":
        do_attack(nm, str(command), str(log))
    else:
        print("Not ready to attack, terminating program")
        exit(0)

    if prnt:
        print_scan(nm)


def scan(ports, hosts):
    nm = nmap.PortScanner()
    if ports == "":
        nm.scan(hosts=hosts)
    else:
        nm.scan(ports=ports, hosts=hosts)
    return nm


def print_scan(nm):
    print(nm.all_hosts())
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

                if "nikto" in command:
                    command = base_command + " -host " + host + " -p " + str(port)
                    print(command)

                subprocess.Popen(command, stdout=out, shell=True).wait()


def create_log(log):
    if os.path.isdir(log):
        log_dir = log
        now = datetime.datetime.now()
        out = open(
            log_dir + "/ATK_OUT_LOG" + now.strftime("%Y-%m-%d--%H-%M-%S") + ".txt", "a"
        )
        out.write("STDOUT FILE FOR " + now.strftime("%Y-%m-%d--%H-%M-%S") + " ATTACK")
        out.flush()
        return out


if __name__ == "__main__":
    main()