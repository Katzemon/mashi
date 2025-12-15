import io

import cairosvg
from PIL import Image

from utils.helpers.svg_helper import remove_redundant_info

resample_mode = Image.Resampling.LANCZOS


def _is_svg(trait):
    return type(trait) is str and "<svg" in trait.lower()


def _svg_bytes_to_img(svg_bytes, target_size=None):
    svg_bytes = remove_redundant_info(svg_bytes)
    png_bytes = cairosvg.svg2png(bytestring=svg_bytes)

    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    if target_size:
        img = img.resize(target_size, resample=resample_mode)

    return img


def get_combined_img_bytes(
        sorted_traits: list,
        bg_size=(1104, 1472),
        overlay_size=(760, 1200),
        is_minted=False
):
    if not sorted_traits:
        raise ValueError("No traits found")

    # selecting base img
    bg_trait = sorted_traits[0]
    base = Image.open(io.BytesIO(bg_trait)).convert("RGBA")
    base = base.resize(bg_size, resample=resample_mode)

    minted_trait = None
    if is_minted:
        minted_trait = sorted_traits.pop()

    for layer in sorted_traits[1:]:
        if _is_svg(layer):
            overlay = _svg_bytes_to_img(layer, target_size=overlay_size)
        else:
            overlay = Image.open(io.BytesIO(layer)).convert("RGBA")
            overlay = overlay.resize(overlay_size, resample=resample_mode)

        ow, oh = overlay.size
        x = (base.width - ow) // 2
        y = (base.height - oh) // 2
        base.alpha_composite(overlay, (x, y))

    if minted_trait:
        overlay = _svg_bytes_to_img(minted_trait, target_size=bg_size)
        base.alpha_composite(overlay, (0, 0))

    # get png bytes
    output_bytes = io.BytesIO()
    base.save(output_bytes, format="PNG")
    return output_bytes.getvalue()
