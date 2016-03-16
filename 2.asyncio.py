#!/usr/bin/env python3

import asyncio
import numpy as np

APP_PORT = 50000
LISTEN_BACKLOG = 1000000

LOGIN_SERVER = '52.17.32.15'
LOGIN_PORT = 50001

ACCOUNTS = 10
SECURITIES = 10000

loop = asyncio.get_event_loop()

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


class EchoServerClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        asyncio.async(self.process_data(data))

    @asyncio.coroutine
    def process_data(self, message):
        action = tuple(map(int, message.split()))

        yield from self.login()

        group = action[0]

        data = manage_account(accounts[group], action)        

        self.transport.write(data.encode())
        self.transport.close()

    @asyncio.coroutine
    def login(self):
        reader, writer = yield from asyncio.open_connection(LOGIN_SERVER, LOGIN_PORT, loop=loop)

        writer.write('login'.encode())

        data = yield from reader.read(1024)

        writer.close()


loop = asyncio.get_event_loop()
coro = loop.create_server(EchoServerClientProtocol, '', APP_PORT)
server = loop.run_until_complete(coro)

print('Serving on {}'.format(server.sockets[0].getsockname()))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

# Close the server
server.close()
loop.run_until_complete(server.wait_closed())
loop.close()

