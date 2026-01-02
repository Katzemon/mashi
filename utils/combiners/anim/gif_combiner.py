import subprocess
import base64
import json
import asyncio
import os

def get_mime_type(data: bytes) -> str:
    """Detects the MIME type based on file signatures (magic bytes)."""
    # Check for SVG (usually starts with <svg or <?xml)
    if data.startswith(b'<svg') or data.startswith(b'<?xml'):
        return "image/svg+xml"
    # Check for WebP (RIFF....WEBP)
    if data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        return "image/webp"
    # Check for PNG / APNG (They share the same header)
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        return "image/png"
    # Check for GIF
    if data.startswith(b'GIF87a') or data.startswith(b'GIF89a'):
        return "image/gif"

    return "image/png"

async def get_combined_gif(
        sorted_traits: list,
        bg_size=(552, 736),
        overlay_size=(380, 600),
        img_type: int = 0,
        is_minted=False,
):
    # 1. Prepare Base64 Data URIs
    b64_images = []
    for trait_bytes in sorted_traits:
        mime_type = get_mime_type(trait_bytes)
        encoded = base64.b64encode(trait_bytes).decode('utf-8')
        b64_images.append(f"data:{mime_type};base64,{encoded}")

    # 2. Get absolute path to the js file in the same folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    js_path = os.path.join(current_dir, 'gif.js')

    try:
        # 3. Setup the subprocess
        process = await asyncio.create_subprocess_exec(
            'node', js_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # 4. Stream data to Node.js
        input_json = json.dumps(b64_images).encode('utf-8')
        stdout, stderr = await process.communicate(input=input_json)

        if process.returncode == 0:
            if not stdout:
                print("Node.js returned success but empty stdout.")
                return None

            gif_size_mb = len(stdout) / (1024 * 1024)
            print(f"Successfully generated GIF. Size: {gif_size_mb:.2f} MB")
            return stdout
        else:
            error_message = stderr.decode('utf-8')
            print(f"Node.js Error:\n{error_message}")
            return None

    except Exception as e:
        print(f"Python Subprocess Error: {e}")
        return None