import torch
import transformers
import os
import glob
import argparse

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
        help="the path containing all the audio segments in .mp3 format.",
    )

    parser.add_argument(
        "--transcripts",
        required=False,
        type=str,
        default="transcripts",
        help="the directory where the transcripts for each segment will be stored.",
    )

    args = parser.parse_args()

    segments = args.segments
    transcripts = args.transcripts

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model = transformers.AutoModelForSpeechSeq2Seq.from_pretrained(
        "distil-whisper/distil-medium.en",
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        use_safetensors=True,
    )
    model.to(device)

    processor = transformers.AutoProcessor.from_pretrained(
        "distil-whisper/distil-medium.en"
    )

    pipe = transformers.pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=128,
        torch_dtype=torch_dtype,
        device=device,
    )

    files = glob.glob(f"{segments}/*.mp3")
    basenames = list(map(lambda x: os.path.basename(x).split(".")[0], files))
    dirname = list(set(map(lambda x: os.path.dirname(x), files)))[0]
    output_dir = os.path.join(dirname, "..", transcripts)

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
            output_path = os.path.join(output_dir, f"{basenames[idx]}.txt")
            res = pipe(f)
            txt = res["text"]

            with open(output_path, "w", encoding="utf-8") as fp:
                fp.write(txt)

            prog_bar.update(task, advance=1)
