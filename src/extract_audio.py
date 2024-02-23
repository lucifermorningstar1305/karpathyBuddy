import os
import glob
import argparse


from moviepy.editor import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
from rich.progress import (
    Progress,
    MofNCompleteColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--segments",
        required=True,
        type=str,
        help="the path containing all the video segments in .mp4 format.",
    )

    parser.add_argument(
        "--audios",
        required=False,
        type=str,
        default="audio_segments",
        help="the directory where the transcripts for each segment will be stored.",
    )

    args = parser.parse_args()

    segments = args.segments
    audios = args.audios

    files = glob.glob(f"{segments}/*.mp4")
    basenames = list(map(lambda x: os.path.basename(x).split(".")[0], files))
    dirname = list(set(map(lambda x: os.path.dirname(x), files)))[0]
    output_dir = os.path.join(dirname, "..", audios)

    prog_bar = Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("◦"),
        TimeElapsedColumn(),
        TextColumn("◦"),
        TimeRemainingColumn(),
        expand=False,
    )

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    with prog_bar as pbar:
        task = pbar.add_task(description="Extracting Audio...", total=len(files))

        for idx, f in enumerate(files):
            output_path = os.path.join(output_dir, f"{basenames[idx]}.mp3")
            ffmpeg_extract_audio(inputfile=f, output=output_path)
            prog_bar.update(task, advance=1)
