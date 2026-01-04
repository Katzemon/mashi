import asyncio
from pathlib import Path

from data.db import db
from gif.gif_service import GifService
from servers.bot_http_server import start_http_server
from servers.bot_server import start_https_server

PROJECT_ROOT = Path(__file__).resolve().parent


async def main():
    db.init()
    await GifService.get_instance().start()

    server_task = asyncio.to_thread(start_https_server)
    http_server_task = asyncio.to_thread(start_http_server)

    await asyncio.gather(server_task, http_server_task)


if __name__ == '__main__':
    asyncio.run(main())
