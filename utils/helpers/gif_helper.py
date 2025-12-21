import io

from PIL import Image


def is_gif(image_bytes: bytes) -> bool:
    try:
        return image_bytes.startswith(b"GIF87a") or image_bytes.startswith(b"GIF89a")
    except Exception as e:
        print(e)
        return False


def extract_first_frame(gif_bytes: bytes) -> bytes:
    with Image.open(io.BytesIO(gif_bytes)) as img:
        img.seek(0)  # first frame

        # Convert to RGB to avoid palette issues
        frame = img.convert("RGB")

        output = io.BytesIO()
        frame.save(output, format="PNG")  # or JPEG
        return output.getvalue()