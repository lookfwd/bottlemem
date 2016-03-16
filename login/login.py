#!/usr/bin/env python3

import asyncio

DELAY_SEC = 0.01

cnt = [0]

class EchoServerClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        asyncio.async(self.process_data(data))

    @asyncio.coroutine
    def process_data(self, data):
        yield from asyncio.sleep(DELAY_SEC)
        self.transport.write(data)
        self.transport.close()
        cnt[0] += 1
        if cnt[0] % 1000 == 0:
            print("%d" % cnt[0])

loop = asyncio.get_event_loop()
# Each client connection will create a new protocol instance
coro = loop.create_server(EchoServerClientProtocol, '', 50001)
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
