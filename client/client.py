#!/usr/bin/env python3

import socket
from random import randint
from timeit import default_timer as time

APP_HOST = '54.78.237.213'
APP_PORT = 50000

import sys
TOTAL_COUNT = int(sys.argv[1])


import concurrent
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

WORKERS = 8
SECURITIES = 10000

def do_req():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((APP_HOST, APP_PORT))

    group = randint(0, 9)
    buy = randint(0, 1)
    quantity = randint(0, 400)
    id = randint(0, SECURITIES-1)

    s.sendall(("%d %d %d %d" % (group, buy, quantity, id)).encode())
    data = s.recv(1024)

    s.close()

def batch_reqs(batch_size):
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        for i in range(batch_size):
            executor.submit(do_req)
        executor.shutDown()

batch_size = int(TOTAL_COUNT / WORKERS)
tci = TOTAL_COUNT

t_start = time()

with concurrent.futures.ProcessPoolExecutor(max_workers=WORKERS) as executor:
    while tci:
        todo = min(tci, batch_size)
        executor.submit(batch_reqs, todo)
        tci -= todo

all_time = time() - t_start

print("total: %d" % TOTAL_COUNT)
print("time: %3.2f" % all_time)
print("time/pc: %5.4f" % (all_time / TOTAL_COUNT))

