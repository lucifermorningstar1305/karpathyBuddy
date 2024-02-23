import os
import re
import argparse
import glob


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
        "--transcriptions",
        required=True,
        type=str,
        help="the directory containing all the transcriptions",
    )
    parser.add_argument(
        "--final",
        required=False,
        type=str,
        default="combined",
        help="name of the transcription file to be saved as.",
    )

    args = parser.parse_args()

    transcriptions = args.transcriptions
    combined_dir = args.final

    files = glob.glob(f"{transcriptions}/*.txt")
    files = sorted(files, key=lambda x: float(re.findall("(\d+)", x)[0]))

    dirname = list(set(map(lambda x: os.path.dirname(x), files)))[0]
    output_dir = os.path.join(dirname, "..", combined_dir)

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
        task = pbar.add_task(description="Transcribing...", total=len(files))

        for idx, f in enumerate(files):
            output_path = os.path.join(output_dir, f"complete_transcript.txt")
            with open(f, "r", encoding="utf-8") as fp:
                txt_data = fp.read()

            with open(output_path, "a+", encoding="utf-8") as fp:
                fp.write(txt_data)

            prog_bar.update(task, advance=1)
