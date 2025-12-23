import re


def generate_minted_svg(nft_name: str) -> bytes:
    pattern = r"(.+)\s+by\s+(.+)"
    match = re.match(pattern, nft_name)
    if match:
        before_by = match.group(1)  # Text before "by"
    else:
        before_by = nft_name

    return (f"""<svg xmlns="http://www.w3.org/2000/svg" width="1104" height="1472">
    <rect width="100%" height="100%" fill="none"/>
    <text 
        x="48" 
        y="{1472 - 48}" 
        font-size="72" 
        font-weight="bold"
        fill="white" 
        stroke="black" 
        stroke-width="3"
    >
        {before_by}
    </text>
</svg>""".encode("utf-8"))