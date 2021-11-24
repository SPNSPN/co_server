#! /usr/bin/env python3

import time
import argparse
import socket
import contextlib
from enum import Enum

class RC (Enum):
	OK = 1
	FEED = 2
	ERROR = 3

def parse_cmd_args ():
	parser = argparse.ArgumentParser()
	parser.add_argument("--addr1", default = "127.0.0.1:4001", help = "address of client1 <ip addr>:<port>")
	parser.add_argument("--addr2", default = "127.0.0.1:4002", help = "address of client2 <ip addr>:<port>")
	return parser.parse_args()

def wait_connection (addr):
	isock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ip, port = addr.split(":")
	isock.bind((ip, int(port)))
	isock.listen(5)
	sock, address = isock.accept()
	sock.setblocking(False)
	return sock

def nonblock_recv (sock):
	msg = b""
	try:
		msg = sock.recv(4096)
	except Exception as e:
		if 10035 == e.args[0]: # WOULDBLOCK
			pass
		elif 11 == e.args[0]: # EAGAIN
			pass
		else:
			raise e
	return msg


def delivery (sock1, sock2):
	while True:
		msg = nonblock_recv(sock1)
		if len(msg) > 0:
			print("recv from {0}: {1}".format(sock1, msg))
			sock2.send(msg)
		yield RC.FEED

def get_unixtime_ms ():
	return int(time.time() * 1000)

def ticking (interval_ms):
	prev_ms = get_unixtime_ms()
	while True:
		curr_ms = get_unixtime_ms()
		elapsed_ms = curr_ms - prev_ms
		rest_ms = max(0, interval_ms - elapsed_ms)
		time.sleep(rest_ms / 1000.0)
		prev_ms = curr_ms
		yield RC.FEED

def main (args):
	with contextlib.ExitStack() as estack:
		sock1 = estack.enter_context(wait_connection(args.addr1))
		sock2 = estack.enter_context(wait_connection(args.addr2))
		deliver1 = delivery(sock1, sock2)
		deliver2 = delivery(sock2, sock1)
		ticker = ticking(100)
		print("start service: {0}, {1}".format(args.addr1, args.addr2))
		while True:
			rc = RC.OK
			rc = rc if RC.ERROR == rc else next(deliver1)
			rc = rc if RC.ERROR == rc else next(deliver2)
			rc = rc if RC.ERROR == rc else next(ticker)
			if RC.OK == rc:
				pass
			elif RC.FEED == rc:
				pass
			elif RC.ERROR == rc:
				break

if __name__ == "__main__":
	main(parse_cmd_args())

