import argparse
import os
from pathlib import Path

os.environ["CHROMA_DB_PATH"] = str(Path(__file__).parent.parent / "chroma.db")

from functions import (  # noqa: E402
    download_transcript,
    summarize_transcript,
    save_summary_to_database,
    get_summary_from_database,
)


def main(link: str):
    transcript = download_transcript(link)
    summary = summarize_transcript(link, transcript)
    save_summary_to_database(link, summary)
    summary = get_summary_from_database(link)
    print("===== Youtube Link =====")
    print(link)
    print("===== Summary =====")
    print(summary)


if __name__ == "__main__":
    # parse a string argument as a youtube link
    parser = argparse.ArgumentParser()
    parser.add_argument("link", help="Youtube video link", default="https://www.youtube.com/watch?v=Oq46-UCWuZ4")
    args = parser.parse_args()
    link = args.link
    main(link)
