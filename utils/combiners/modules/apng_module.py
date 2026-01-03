import io

from apng import APNG


def is_apng(image_bytes):
    try:
        buffer = io.BytesIO(image_bytes)
        im = APNG.open(buffer)

        return len(im.frames) > 1
    except Exception as e:
        print(e)
        return False
