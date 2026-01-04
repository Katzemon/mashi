import asyncio

from servers.bot_http_server import start_http_server
from servers.bot_server import start_https_server


async def main():
    server_task = asyncio.to_thread(start_https_server)
    http_server_task = asyncio.to_thread(start_http_server)

    await asyncio.gather(server_task, http_server_task)


if __name__ == '__main__':
    asyncio.run(main())
