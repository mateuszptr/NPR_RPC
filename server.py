import asyncio
import re
import sys

from rpcudp.protocol import RPCProtocol

curr_id = 0
commands = {}
args = sys.argv[1:]
saddr = (str(args[0]), int(args[1]))
caddr = (str(args[0]), int(args[2]))


async def send_output_line(line, addr):
    global cprotocol
    while True:
        result = await cprotocol.output(addr, line)
        if result[0]: break


async def send_stream(stream, addr):
    while True:
        line = await stream.readline()
        if line:
            print("Got a line")
            line = line.decode('utf8')
            print("Decoded a line")
            lines = re.findall('.{1,100}', line)
            print("Chunked a line")
            for line in lines:
                await send_output_line(line, addr)
                print("Sent a line: %s", line)
        else:
            break


async def handle_cmd(id):
    global commands, cprotocol
    print(commands)
    print(id)
    await asyncio.wait([
        send_stream(commands[id][0].stdout, commands[id][1]),
        send_stream(commands[id][0].stderr, commands[id][1])
    ])

    result = await commands[id][0].wait()
    result = await cprotocol.end(commands[id][1], result)
    del commands[id]

    return result


class RPCServer(RPCProtocol):
    def rpc_sayhi(self, sender, name):
        return "Hello %s you live at %s:%i" % (name, sender[0], sender[1])

    async def rpc_cmd(self, sender, backaddr, cmd):
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE,
                                                        stderr=asyncio.subprocess.PIPE, stdin=asyncio.subprocess.PIPE)

        global curr_id, commands
        curr_id += 1
        commands[curr_id] = (process, (backaddr[0], backaddr[1]))
        asyncio.ensure_future(handle_cmd(curr_id))

        return curr_id

    async def rpc_input(self, sender, id, data):
        global commands
        print("Writing %s to id: %d" % (data, id))
        try:
            commands[id][0].stdin.write(data.encode('utf8'))
            await commands[id][0].stdin.drain()
        finally:
            return id

    async def rpc_eof(self, sender, id):
        global commands
        commands[id][0].stdin.write_eof()
        return id

    async def rpc_kill(self, sender, id):
        global commands
        commands[id][0].kill()
        return id


loop = asyncio.get_event_loop()
listen = loop.create_datagram_endpoint(RPCServer, local_addr=saddr)
transport, protocol = loop.run_until_complete(listen)
clisten = loop.create_datagram_endpoint(RPCProtocol, local_addr=caddr)
ctransport, cprotocol = loop.run_until_complete(clisten)

try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

transport.close()
loop.close()
