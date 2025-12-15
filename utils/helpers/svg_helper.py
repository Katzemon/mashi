import re


def remove_redundant_info(svg: str) -> str:
    svg = re.sub(r"<\?xml.*?\?>", "", svg)
    svg = re.sub(r"<!DOCTYPE.*?>", "", svg)
    svg = re.sub(r'serif:[^"]*"[^"]*"', '', svg)
    svg = re.sub(r'<sodipodi:namedview\b[^>]*?>[\s\S]*?<\/sodipodi:namedview>', '', svg)
    svg = re.sub(r"<sodipodi:namedview\b[^>]*/>", "", svg)
    svg = re.sub(r'\s*sodipodi:[^=]+="[^"]*"', '', svg)
    svg = re.sub(r'\s*inkscape:[^=]+="[^"]*"', '', svg)
    svg = re.sub(r'<SODI[^>]*>', '', svg)
    svg = re.sub(r'<!--.*?-->', '', svg)
    return svg.strip()


def replace_colors(svg_str: str, body_color: str, eyes_color: str, hair_color: str) -> str:
    # replace body color
    svg_str = re.sub(
        r"#00ff00|#0f0\b|\blime\b|rgb\s*\(\s*0\s*,\s*255\s*,\s*0\s*\)",
        body_color, svg_str, flags=re.IGNORECASE
    )

    # replace eyes color
    svg_str = re.sub(
        r"#ffff00|#ff0\b|\byellow\b|rgb\s*\(\s*255\s*,\s*255\s*,\s*0\s*\)",
        eyes_color, svg_str, flags=re.IGNORECASE
    )

    # replace hair color
    svg_str = re.sub(
        r"#0000ff|#00f\b|\bblue\b|rgb\s*\(\s*0\s*,\s*0\s*,\s*255\s*\)",
        hair_color, svg_str, flags=re.IGNORECASE
    )
    return svg_str
