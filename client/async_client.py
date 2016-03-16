#!/usr/bin/env python3

import asyncio
import pandas
import numpy as np
from random import randint
from timeit import default_timer as time

APP_HOST = '54.78.237.213'
APP_PORT = 50000

import sys
TOTAL_COUNT = int(sys.argv[1])

stats_total_time = []
stats_wait_time = []
cnt = [0]

loop = asyncio.get_event_loop()

class TraderProtocol(asyncio.Protocol):
    def __init__(self):
        self.t_start = time()

    def connection_made(self, transport):
        wait_time = time() - self.t_start
        stats_wait_time.append(wait_time)
        message = str(randint(0, 9)) 
        transport.write(message.encode())

    def data_received(self, data):
        latency = time() - self.t_start
        stats_total_time.append(latency)

    def connection_lost(self, exc):
        cnt[0] += 1
        if cnt[0] == TOTAL_COUNT:
            loop.stop()


t_start = time()

for i in range(TOTAL_COUNT):
    tp = TraderProtocol()
    coro = loop.create_connection(lambda: tp, APP_HOST, APP_PORT)
    loop.run_until_complete(coro)

loop.run_forever()
loop.close()

assert len(stats_total_time) == TOTAL_COUNT

all_time = time() - t_start

def to_stats(df, stats):
    df.loc[df.shape[0]] = [
        np.average(stats),
        np.percentile(stats, 50),
        np.percentile(stats, 95),
        np.percentile(stats, 99)
    ]

df = pandas.DataFrame({}, columns=['average', '50pct', '95pct', '99pct'])
to_stats(df, stats_wait_time)
to_stats(df, stats_total_time)
df = df.applymap(lambda x: x * 1000)
df.index = pandas.Index(['wait time', 'overall time'])

print("total: %d" % TOTAL_COUNT)
print("time: %3.2f" % all_time)
print("time/pc: %5.4f" % (all_time / TOTAL_COUNT))
print(df)

