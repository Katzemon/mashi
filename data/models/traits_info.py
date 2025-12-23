from dataclasses import dataclass

from data.models.image_format import ImageFormat


@dataclass
class TraitsInfo:
    frames: int
    frame_t: float
    total_t: float
    is_animated: bool