import subprocess
import base64
import json
import asyncio
import os

# 1. Initialize the Semaphore globally to limit concurrency to 2
process_limit = asyncio.Semaphore(2)

def get_mime_type(data: bytes) -> str:
    # ... (Keep your existing get_mime_type code here) ...
    if data.startswith(b'<svg') or data.startswith(b'<?xml'): return "image/svg+xml"
    if data.startswith(b'RIFF') and data[8:12] == b'WEBP': return "image/webp"
    if data.startswith(b'\x89PNG\r\n\x1a\n'): return "image/png"
    if data.startswith(b'GIF87a') or data.startswith(b'GIF89a'): return "image/gif"
    return "image/png"

async def get_combined_gif(
        sorted_traits: list,
        bg_size=(552, 736),
        overlay_size=(380, 600),
        img_type: int = 0,
        is_minted=False,
):
    # 2. Use the Semaphore context manager
    # This will automatically queue any calls beyond the first 2
    async with process_limit:
        # Prepare Base64 Data URIs
        b64_images = []
        for trait_bytes in sorted_traits:
            mime_type = get_mime_type(trait_bytes)
            encoded = base64.b64encode(trait_bytes).decode('utf-8')
            b64_images.append(f"data:{mime_type};base64,{encoded}")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        js_path = os.path.join(current_dir, 'gif.js')

        try:
            process = await asyncio.create_subprocess_exec(
                'node', js_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            input_json = json.dumps(b64_images).encode('utf-8')
            stdout, stderr = await process.communicate(input=input_json)

            if process.returncode == 0:
                if not stdout:
                    return None
                print(f"Generated GIF: {len(stdout) / (1024 * 1024):.2f} MB")
                return stdout
            else:
                print(f"Node.js Error: {stderr.decode('utf-8')}")
                return None

        except Exception as e:
            print(f"Python Subprocess Error: {e}")
            return None