import io
from typing import Tuple

from PIL import Image
from apng import APNG


def check_if_apng(image_bytes):
    try:
        buffer = io.BytesIO(image_bytes)
        im = APNG.open(buffer)

        return len(im.frames) > 1
    except Exception as e:
        print(e)
        return False


def get_apng_info(image_bytes) -> Tuple[int, float]:
    """
    Returns number of frames, total duration in seconds
    """
    im = APNG.open(io.BytesIO(image_bytes))
    num_frames = len(im.frames)
    total_duration = 0

    for png, control in im.frames:
        if control:
            # Duration in seconds = delay / delay_den
            # If delay_den is 0, it defaults to 100 per spec
            denom = control.delay_den if control.delay_den != 0 else 100
            total_duration += control.delay / denom

    return num_frames, total_duration


def get_frames_as_bytes(data_bytes):
    """
    Returns a list of PNG bytes for each frame of an APNG (or a static PNG),
    normalized to full canvas size (each frame is a full PNG image).
    """
    im = APNG.open(io.BytesIO(data_bytes))
    frames_bytes = []

    # Handle static PNG
    if not im.frames:
        frames_bytes.append(data_bytes)
        return frames_bytes

    # Get full canvas size from the first frame
    first_png, first_control = im.frames[0]
    first_frame = Image.open(io.BytesIO(first_png.to_bytes())).convert("RGBA")
    canvas_width, canvas_height = first_frame.size

    # Create a blank RGBA canvas for cumulative frame composition
    prev_frame = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))

    for png, control in im.frames:
        frame = Image.open(io.BytesIO(png.to_bytes())).convert("RGBA")

        # Offsets (0 if control is None)
        x_offset = control.x_offset if control else 0
        y_offset = control.y_offset if control else 0

        # Create a copy of previous frame to apply this frame's changes
        full_frame = prev_frame.copy()
        full_frame.paste(frame, (x_offset, y_offset), frame)  # paste with alpha mask

        # Convert to PNG bytes
        b = io.BytesIO()
        full_frame.save(b, format="PNG")
        frames_bytes.append(b.getvalue())

        # Update prev_frame for next iteration
        prev_frame = full_frame

    return frames_bytes