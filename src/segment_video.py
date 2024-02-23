"""
Credit: https://medium.com/@henryreith/split-your-video-files-into-x-second-parts-for-instagram-friendly-segments-using-python-ea0f7fd1dad0
"""

import os
import sys
import argparse

from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from moviepy.editor import VideoFileClip


def split_video_clip(filename: str, segment_length: int, output_dir: str):
    """Function to split the video file into different segments"""

    clip = VideoFileClip(filename)

    duration = clip.duration

    start_time = 0
    end_time = segment_length

    counter = 0

    basename = os.path.basename(filename).split(".")[0]
    dir_path = os.path.dirname(filename)

    output_path = os.path.join(dir_path, output_dir)

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    print(output_path, basename)

    while start_time < duration:
        output = os.path.join(output_path, f"{basename}_part_{counter}.mp4")
        ffmpeg_extract_subclip(
            filename=filename,
            t1=start_time,
            t2=min(end_time, duration),
            targetname=output,
        )

        start_time = end_time
        end_time += segment_length
        counter += 1

        print(f"Video added to {output}")

    print(f"Video split into {counter - 1} parts")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--video_path", required=True, type=str, help="the path of the video file."
    )

    parser.add_argument(
        "--segment",
        required=False,
        type=int,
        default=5,
        help="the splitting segment length (in seconds)",
    )

    parser.add_argument(
        "--output_dir",
        required=False,
        type=str,
        default="segments",
        help="the output directory name.",
    )

    args = parser.parse_args()

    video_path = args.video_path
    segment = args.segment
    output_dir = args.output_dir

    split_video_clip(filename=video_path, segment_length=segment, output_dir=output_dir)
