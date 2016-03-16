#!/usr/bin/env python3

import socket
from time import sleep

APP_PORT = 50000
LISTEN_BACKLOG = 1000000

LOGIN_SERVER = '52.17.32.15'
LOGIN_PORT = 50001

def login():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((LOGIN_SERVER, LOGIN_PORT))

    s.sendall(('login').encode())
    data = s.recv(1024)

    s.close()


def initListening():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', APP_PORT))
    s.listen(LISTEN_BACKLOG)
    return s

SECURITIES = 10000

import threading
lock = threading.RLock()
import numpy as np
accounts = [np.random.randint(0, 1000, SECURITIES) for i in range(10)]

def manage_account(account, action):
    group, buy, quantity, id = action

    if (not buy) and quantity > account[id]:
        return "can't sell"

    if buy:
        account[id] += quantity
    else:
        account[id] -= quantity

    return "ok"


def business_logic(data):
    action = tuple(map(int, data.split()))

    login()

    group = action[0]

    with lock:
        return manage_account(accounts[group], action)

def serve(conn):
    request = conn.recv(1024)

    resp = business_logic(request)

    conn.sendall(resp.encode())
    conn.close()


s = initListening()

import concurrent 
from concurrent.futures import ThreadPoolExecutor
with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
    while True:
        conn, addr = s.accept()
        #serve(conn)
        executor.submit(serve, conn)

