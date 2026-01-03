import io

from PIL import Image


def is_gif(data) -> bool:
    return data.startswith(b"GIF87a") or data.startswith(b"GIF89a")


def extract_first_gif_frame(gif_bytes: bytes) -> bytes:
    try:
        with Image.open(io.BytesIO(gif_bytes)) as img:
            img.seek(0)  # first frame

            # Convert to RGB to avoid palette issues
            frame = img.convert("RGB")

            output = io.BytesIO()
            frame.save(output, format="PNG")
            return output.getvalue()
    except Exception as e:
        print(e)
