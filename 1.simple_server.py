#!/usr/bin/env python3

import socket
from time import sleep

APP_PORT = 50000
LISTEN_BACKLOG = 100000

LOGIN_SERVER = '52.17.32.15'
LOGIN_PORT = 50001

def login(data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((LOGIN_SERVER, LOGIN_PORT))

    s.sendall(('login-%d' % data).encode())
    data = s.recv(1024)

    s.close()


def initListening():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', APP_PORT))
    s.listen(LISTEN_BACKLOG)
    return s


def business_logic(data):
    login(data)

    return "ok"

def serve(conn):
    request = int(conn.recv(1024))

    resp = business_logic(request)

    conn.sendall(resp.encode())
    conn.close()


s = initListening()

import concurrent 
from concurrent.futures import ThreadPoolExecutor
with concurrent.futures.ThreadPoolExecutor(max_workers=1000) as executor:
    while True:
        conn, addr = s.accept()
        #serve(conn)
        executor.submit(serve, conn)

