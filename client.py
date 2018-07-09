import asyncio
import re
import sys

from rpcudp.protocol import RPCProtocol


async def send_command(protocol, addr, cmd):
    global caddr_rpc
    result = await protocol.cmd(addr, caddr_rpc, cmd)
    print("### Process started with id=%d ###" % result[1])
    global id
    id = result[1]

    reader = await get_async_stdin_reader()
    await handle_stdin(reader)


async def send_input(protocol, addr, data):
    while True:
        global id
        result = await protocol.input(addr, id, data)
        # print("Sent data '%s' to %s with id [%d]" % (data, addr, id))
        if result[0]: break


async def sayhi(protocol, address):
    result = await protocol.sayhi(address, "Dfewsf")
    print(result[1] if result[0] else "No response :c")


class RPCClient(RPCProtocol):
    def rpc_output(self, sender, data):
        print(data)

    def rpc_end(self, sender, code):
        print("### Process ended with code=%d" % code)
        global loop
        loop.stop()


async def get_async_stdin_reader(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    reader = asyncio.StreamReader()
    reader_proto = asyncio.StreamReaderProtocol(reader)

    await loop.connect_read_pipe(lambda: reader_proto, sys.stdin)

    return reader


async def handle_stdin(reader):
    global protocol, saddr, id
    while True:
        line = await reader.readline()
        if line:
            # print(line)
            line = line.decode('utf8')
            # print(line)
            chunks = re.findall("[\s\S]{1,100}", line)
            for chunk in chunks:
                # print(chunk)
                await send_input(protocol, saddr, chunk)
        else:
            break
    await protocol.eof(saddr, id)


args = sys.argv[1:]
cmd = str(args[0])
id = -1
saddr = (str(args[1]), int(args[2]))
caddr = (str(args[3]), int(args[4]))
caddr_rpc = (str(args[3]), int(args[5]))

loop = asyncio.get_event_loop()

listen = loop.create_datagram_endpoint(RPCProtocol, local_addr=caddr)
transport, protocol = loop.run_until_complete(listen)

slisten = loop.create_datagram_endpoint(RPCClient, local_addr=caddr_rpc)
stransport, sprotocol = loop.run_until_complete(slisten)

# func = sayhi(protocol, ('127.0.0.1', 1234))
# loop.run_until_complete(func)

func = send_command(protocol, saddr, cmd)
# try:
try:
    loop.run_until_complete(func)
    loop.run_forever()
except:
    pass
# except:
#     pass

transport.close()
loop.close()
