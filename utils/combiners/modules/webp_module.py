import io
from typing import Tuple

import imageio
from PIL import Image, ImageSequence


def is_webp(data: bytes) -> bool:
    """
    Detects whether the given bytes represent a WebP file.
    """
    return data.startswith(b"RIFF") and data[8:12] == b"WEBP"


def extract_first_webp_frame(webp_bytes: bytes) -> bytes:
    """
    Extracts the first frame of a (possibly animated) WebP
    and returns it as PNG bytes.
    """
    try:
        with Image.open(io.BytesIO(webp_bytes)) as img:
            img.seek(0)

            frame = img.convert("RGBA")
            output = io.BytesIO()
            frame.save(output, format="PNG")

            return output.getvalue()
    except Exception as e:
        print(e)
        return b""
