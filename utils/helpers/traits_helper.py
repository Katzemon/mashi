import asyncio

from data.models.traits_info import TraitsInfo
from utils.helpers.apng.apng_helper import get_apng_info, is_apng
from utils.helpers.constants import ANIM_STEP
from utils.helpers.gif.gif_helper import is_gif, get_gif_info
from utils.helpers.math_helper import correct_timing
from utils.helpers.webp.webp_helper import is_webp, get_webp_info

async def process_trait(trait):
    if is_apng(trait):
        num_frames, total_duration = await asyncio.to_thread(get_apng_info, trait)
        frame_t = correct_timing(total_duration / num_frames)
        total_duration = round(frame_t * num_frames, 2)
        return TraitsInfo(frames=num_frames, frame_t=frame_t, total_t=total_duration, is_animated=True), total_duration
    elif is_gif(trait):
        num_frames, total_duration = await asyncio.to_thread(get_gif_info, trait)
        frame_t = correct_timing(total_duration / num_frames)
        total_duration = round(frame_t * num_frames, 2)
        return TraitsInfo(frames=1, frame_t=frame_t, total_t=total_duration, is_animated=True), total_duration
    elif is_webp(trait):
        num_frames, total_duration = await asyncio.to_thread(get_webp_info, trait)
        frame_t = correct_timing(total_duration / num_frames)
        total_duration = round(frame_t * num_frames, 2)
        return TraitsInfo(frames=1, frame_t=frame_t, total_t=total_duration, is_animated=True), total_duration
    else:
        return TraitsInfo(frames=1, frame_t=ANIM_STEP, total_t=ANIM_STEP, is_animated=False), ANIM_STEP


async def get_traits_info(sorted_traits):
    tasks = [process_trait(trait) for trait in sorted_traits]
    results = await asyncio.gather(*tasks)
    traits_info, total_ts = zip(*results)
    return list(traits_info), list(total_ts)
