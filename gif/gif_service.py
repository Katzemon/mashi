import asyncio
import base64

import httpx

from utils.helpers.traits_helper import get_traits_info
from configs.config import MAX_GIF_GENERATIONS_AT_TIME, GIF_MAKER_SERVER_URI


def get_mime_type(data: bytes) -> str:
    # ... (Keep your existing get_mime_type code here) ...
    if data.startswith(b'<svg') or data.startswith(b'<?xml'): return "image/svg+xml"
    if data.startswith(b'RIFF') and data[8:12] == b'WEBP': return "image/webp"
    if data.startswith(b'\x89PNG\r\n\x1a\n'): return "image/png"
    if data.startswith(b'GIF87a') or data.startswith(b'GIF89a'): return "image/gif"
    return "image/png"


class GifService:
    _instance = None

    def __init__(self):
        if GifService._instance is not None:
            raise Exception("This class is a singleton! Use GifService.get_instance()")
        self.semaphore = asyncio.Semaphore(MAX_GIF_GENERATIONS_AT_TIME) #defines max GIF generations at time

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    async def create_gif(self, trait_buffers: list, length=1):
        total_ts = await get_traits_info(trait_buffers)
        max_t = max(total_ts)

        async with self.semaphore:
            images = []
            for buf in trait_buffers:
                mime = get_mime_type(buf)
                b64 = base64.b64encode(buf).decode("utf-8")
                images.append(f"data:{mime};base64,{b64}")

            payload = {
                "images": images,
                "max_t": max_t * length,  # 👈 pass timing info
            }

            async with httpx.AsyncClient(timeout=120.0) as client:
                try:
                    response = await client.post(GIF_MAKER_SERVER_URI, json=payload)
                    if response.status_code == 200:
                        return response.content
                    print(f"❌ Service Error: {response.status_code}")
                except Exception as e:
                    print(f"❌ Connection Error: {e}")

            return None
