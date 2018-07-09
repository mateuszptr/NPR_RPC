import asyncio
import sys


async def get_async_stdin_reader(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    reader = asyncio.StreamReader()
    reader_proto = asyncio.StreamReaderProtocol(reader)

    await loop.connect_read_pipe(lambda: reader_proto, sys.stdin)

    return reader


async def read_stream(stream, cb):
    while True:
        line = await stream.readline()
        if line:
            cb(line)
        else:
            break


async def handle_stdin(output, reader):
    while True:
        line = await reader.readline()
        if line:
            output.write(line)
            await output.drain()
        else:
            break

    output.write_eof()


async def write_stream(stream, data):
    stream.write(data)
    # print("Sent data")
    stream.write_eof()
    # print("Sent EOF")


async def stream_subprocess(cmd, stdout_cb, stderr_cb, data):
    process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                                                    stdin=asyncio.subprocess.PIPE)
    reader = await get_async_stdin_reader()

    await asyncio.wait([
        read_stream(process.stdout, stdout_cb),
        read_stream(process.stderr, stderr_cb),
        handle_stdin(process.stdin, reader)
    ])
    # print("Waiting to end\n")
    return await process.wait()


def execute(cmd, stdout_cb, stderr_cb, data):
    loop = asyncio.get_event_loop()
    rc = loop.run_until_complete(stream_subprocess(cmd, stdout_cb, stderr_cb, data))
    loop.close()
    return rc


if __name__ == '__main__':
    print(
        execute("sort | tr [:lower:] [:upper:]",
                lambda x: print("%s" % x),
                lambda x: print("STDERR: %s" % x),
                b'rybka\n')
    )
