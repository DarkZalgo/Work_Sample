#!/usr/bin/env python3

#John Cummings
#ACO 330

import socket
import sys
import os


def main():
    url =''
    if not sys.argv[1:]:
        usage()
        exit(-1)
    if "http://" in sys.argv[1] :
        url = ''.join(sys.argv[1].split('http://')[1:])
        url = url.split('/')
    elif "https://" in sys.argv[1]:
        url = ''.join(sys.argv[1].split('https://')[1:])
        url = url.split('/')
    else:
        url = str(sys.argv[1]).split("/")
    path = "/".join(url[1:])
    host = url[0]
    dl_str = url[-1]
    if len(url) == 1:
        dl_str = "index.html"

    if len(sys.argv[2:]):
        if sys.argv[2].isdigit():
            port = int(sys.argv[2])

        else:
            print("\nERROR")
            print("Must input port number as second argument or leave empty\n")
            usage()
            exit(-1)
    else:
        port = 80

    try:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        ip1 = socket.gethostbyname(url[0])
        ip2 = socket.gethostbyname(url[0])

        if ip1==ip2:
            print("Resolving " + url[0] + " as " + socket.gethostbyname(url[0]))
        else:
            print("Resolving " + url[0] + " as " + ip1+", "+ip2)

        sys.stdout.write(
            "Attempting to connect to " + ip1 + ":" + str(port) + "..."
        )

        sock.connect((ip1, port))
        sys.stdout.write("connected\n")
        request = (
            "GET /" + path
            + " HTTP/1.1\r\n"
            + "User-Agent: Python/3.7\r\n"
            + "Accept: */*\r\n"
            + "Accept-Encoding: identity\r\n"
            + "Host: " + host + "\r\n"
            + "Connection: Keep-Alive\r\n\r\n"
        )

        sock.sendall(request.encode())
        sys.stdout.write("HTTP Request sent...")
        sock.settimeout(10)
        data = sock.recv(4096)
        sock.settimeout(None)

        header = data.decode().split("\r\n\r\n")[0]
        headers = header.split("\r\n")

        if "200 OK" not in header:
            print("Error " + " ".join(headers[0].split()[1:]))
            print("Unable to download " + url[-1] + " from " + url[0])
            exit(0)

        sys.stdout.write("Received " + " ".join(headers[0].split()[1:]) + "\n\n")
        current_size = sys.getsizeof(data)
        total_size = 0

        for x in range(len(headers)):
            if "Content-Length" in headers[x]:
                total_size += int(headers[x].split(": ")[1])
                total_size += current_size
        total_data = ""

        sys.stdout.write("%s" % (" " * 40))
        sys.stdout.flush()
        sys.stdout.write("\b" * 41)

        if total_size == 0:
            total_size = 1

        while data:
            num = float(current_size / total_size) * 100
            num = " %03.2f" % num
            sys.stdout.write(
                "\b"
                * (len("/" + str(current_size) + str(total_size)) + len(str(num)) + 1)
            )
            sys.stdout.write("%s/%s" % (current_size, total_size))

            sys.stdout.write(num)
            sys.stdout.write("%")
            sys.stdout.flush()
            total_data += data.decode()
            sock.settimeout(5)
            data = sock.recv(4096)
            sock.settimeout(None)

            current_size += sys.getsizeof(data)
        sys.stdout.write(
            "\b" * (len("/" + str(current_size) + str(total_size)) + len(str(num)) + 1)
        )
        sys.stdout.write("%s/%s" % (total_size, total_size))
        sys.stdout.write(" 100%\033[K")

        sys.stdout.write("\nDownload of " + dl_str + " Complete!\n")
        sys.stdout.write("Saved to " + os.getcwd() + "\n")

        total_data = total_data.split("\r\n\r\n")

        if "200 OK" in headers[0]:
            file = open(dl_str, "w")
            file.write("\r\n\r\n".join(total_data[1:]))

            file.close()

    except socket.timeout:
        sys.stdout.write(
            "\b" * (len("/" + str(current_size) + str(total_size)) + len(str(num)) + 1)
        )
        sys.stdout.write("%s/%s" % (total_size, total_size))
        sys.stdout.write(" 100%\033[K")
        sys.stdout.write("\nDownload of " + url[-1] + " Complete!\n")
        sys.stdout.write("Saved to " + os.getcwd() + "\n")

        if "200 OK" in headers[0]:
            total_data = total_data.split("\r\n\r\n")
            if"200 OK" in headers[0]:
                file = open(dl_str, "w")
                file.write("\r\n\r\n".join(total_data[1:]))

                file.close()
    except socket.gaierror:
        print("Unable to resolve "+url[0])
    except Exception as e:
        print(str(e))
        raise

    finally:
        sock.close()


def usage():
    print("Usage:\t ./web_get.py <URL_PATH_TO_FILE> <PORT> [optional]")
    print("EX:\t./web_get.py gaia.cs.umass.edu/wireshark-labs/alice.txt")
    print("EX:\t./web_get.py 127.0.0.1/Desktop/alice.txt 8000")


if __name__ == "__main__":
    main()
