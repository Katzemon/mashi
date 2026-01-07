import asyncio

from servers.bot_server import start_https_server


async def main():
    server_task = asyncio.to_thread(start_https_server)

    await asyncio.gather(server_task)


if __name__ == '__main__':
    asyncio.run(main())
