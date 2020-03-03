#!/usr/bin/env python3


import sys
import argparse
import getpass
import os

try:
    from crontab import CronTab
except ModuleNotFoundError:
    print("CronTab module not found")
    install_choice = input("Would you like to install Crontab? Y/N\n")
    if install_choice.lower() == "y" or install_choice.lower == "yes":
        try:
            os.system("pip3 install python-crontab")
        except Exception as e:

            print("Could not install python-crontab module")
            print(e)
            exit(-1)
        print(
            "\npython-crontab module installed successfully\nRunning original command"
        )
        cmdstr = ""
        for arg in sys.argv:
            cmdstr += arg + " "
        os.system(cmdstr)
        exit(0)
    else:
        print("Not installing crontab")
        exit(0)


user = getpass.getuser()
minutes = "0"
hours = "0"
month_day = "0"
month = "0"
week_day = "0"


def main():
    global user
    global minutes
    global hours
    global month_day
    global month
    global week_day
    parser = argparse.ArgumentParser(
        description="Cron Scheduler is a utility to schedule crontabs by specifying the "
        "command used, along with the frequency the command should run"
    )

    parser.add_argument(
        "-cmd",
        metavar="-command",
        nargs="+",
        type=str,
        help="Full command for the crontab to run ending "
        "with comment. Example: -cmd "
        "python /usr/bin/current_date.py todays_date",
    )

    parser.add_argument(
        "-r",
        metavar="-remove",
        type=str,
        help="Remove a specific crontab given the comment",
    )

    parser.add_argument("-ls", action="store_true", help="List all current crontabs")

    parser.add_argument(
        "-u",
        metavar="-user",
        type=str,
        help="User for the Cron Scheduler to write the crontab for. "
        "Default=current user",
    )

    parser.add_argument(
        "-mi", metavar="-minutes", type=int, help="Frequency of crontab in minutes"
    )

    parser.add_argument(
        "-hr", metavar="-hours", type=int, help="Frequency of crontab in hours"
    )

    parser.add_argument(
        "-dm",
        metavar="-day_of_month",
        type=int,
        help="Specific day of month to schedule crontab for " "[1-31]",
    )

    parser.add_argument(
        "-mo",
        metavar="-month",
        type=int,
        help="Specific month to schedule crontab for [1-12]",
    )

    parser.add_argument(
        "-dw",
        metavar="-day_of_week",
        type=int,
        help="Specific day of week to schedule crontab for [0-6]",
    )

    parser.add_argument(
        "-onboot",
        action="store_true",
        help="Set the crontab to run every time on system boot",
    )

    if not len(sys.argv[1:]):
        parser.print_help()

    try:
        args = parser.parse_args()
        cron = CronTab(user=user)
        if args.u:
            user = args.u
        if args.cmd:
            if len(args.cmd) < 2:
                print(
                    "Error: not enough arguments for command.\nDid you forget a comment?"
                )
                exit(-1)
            cmdstr = ""
            comment = args.cmd[-1]

            for i in range(len(args.cmd) - 1):
                cmdstr += str(args.cmd[i])
                if i + 1 < len(args.cmd) - 1:
                    cmdstr += " "

            job = cron.new(command=cmdstr, comment=comment)

        if args.mi:
            minutes = args.mi
            job.minute.every(minutes)

        if args.hr:
            hours = args.hr
            job.hour.every(hours)

        if args.dm:
            month_day = args.dm
            job.day.on(month_day)

        if args.mo:
            month = args.mo
            job.month.during(month)

        if args.dw:
            week_day = args.dw
            job.dow.on(week_day)

        if args.ls:
            for job in cron:
                print(job)

        if args.r:
            cron.remove_all(comment=args.r)

        if args.onboot:
            job.every_reboot()

        cron.write()
    except argparse.ArgumentError as err:
        print(str(err))
        parser.print_usage()


if __name__ == "__main__":
    main()