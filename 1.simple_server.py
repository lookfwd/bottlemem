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

ACCOUNTS = 10
SECURITIES = 10000

import threading
lock = threading.RLock()
import numpy as np
accounts = [np.random.randint(0, 1000, SECURITIES) for i in range(ACCOUNTS)]

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


from multiprocessing import Process, Queue

answer_queue = Queue()
answer_lock = threading.RLock()
answer_registry = {}
answer_cnt = [0]

def answer_manager():
    while True:
        call_id, answer = answer_queue.get()

        with answer_lock:
            queue = answer_registry.pop(call_id)

        queue.put(answer)

import concurrent 
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
answer_thread = Thread(target=answer_manager, args=() )
answer_thread.start()
#answer_thread.join()

processes = []
process_queues = [Queue() for i in range(ACCOUNTS)]

def manage_account_process_thread(call_id, action, account, lock):
    login()

    with lock:
        answer = manage_account(account, action)

    answer_queue.put((call_id, answer))

def manage_account_process(id, queue):
    account = np.random.randint(0, 1000, SECURITIES)
    account_lock = threading.RLock()

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        while True:
            call_id, action = queue.get()

            executor.submit(manage_account_process_thread, call_id, action, account, account_lock)

for id in range(ACCOUNTS):
    p = Process(target=manage_account_process, args=(id, process_queues[id]))
    processes.append(p)
    p.start()

#for i in range(ACCOUNTS):
#    processes[i].join()

import queue

def business_logic_with_proc(data):
    action = tuple(map(int, data.split()))
    group = action[0]

    my_queue = queue.Queue()

    with answer_lock:
        answer_cnt[0] += 1
        my_answer_cnt = answer_cnt[0]
        answer_registry[my_answer_cnt] = my_queue

    process_queues[group].put((my_answer_cnt, action))

    return my_queue.get()


def serve(conn):
    request = conn.recv(1024)

    resp = business_logic_with_proc(request)

    conn.sendall(resp.encode())
    conn.close()


s = initListening()

with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    while True:
        conn, addr = s.accept()
        #serve(conn)
        executor.submit(serve, conn)

