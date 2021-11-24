#! /usr/bin/python

from __future__ import print_function
import sys # for readline, write
import socket
from contextlib import closing

def cmdArguments(args, default_host, default_port):
    if len(args) > 2:
        return args[1], int(args[2])
    if len(args) == 2:
        return args[1], default_port
    return default_host, default_port

def main(args):
    host, port = cmdArguments(args, "127.0.0.1", 4000)

    bufsize = 4096
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("call {0} {1}".format(host, port))
    with closing(sock):
        sock.connect((host, port))
        sys.stdout.write('>>> ') 
        input = sys.stdin.readline()
        sock.send(input)
        msg = sock.recv(bufsize)
        print(msg)
    return

if __name__ == '__main__':
    main(sys.argv)

