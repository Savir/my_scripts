#!/usr/bin/env python3

import argparse
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path


def get_metadata_date(file_path):
    """
    Extracts the creation date metadata using exiftool.
    Returns the oldest date found.
    """
    dates_found = [datetime.now()]

    try:
        result = subprocess.run(
            [
                "exiftool",
                "-s",
                "-s",
                "-s",
                "-DateTimeOriginal",
                "-MediaCreateDate",
                "-CreationDate",
                file_path,
            ],
            capture_output=True,
            text=True,
        )

        output = result.stdout.strip() or ""

        for line in output.splitlines():
            try:
                date_str = line.split("+")[0]
                date_str = re.sub(r"\D", "", date_str)
                dt = datetime.strptime(date_str, "%Y%m%d%H%M%S")
                dates_found.append(dt)
            except ValueError:
                pass

        stat = file_path.stat()

        if hasattr(stat, "st_birthtime"):
            dates_found.append(datetime.fromtimestamp(stat.st_birthtime))
        else:
            dates_found.append(datetime.fromtimestamp(stat.st_ctime))

    except Exception as e:
        print(f"Error reading metadata for {file_path}: {type(e)}: {e}")

    return file_path, min(dates_found)


def rename_files_in_directory(directory, do_action=False):
    """
    Recursively renames media files in directory.

    Each file uses its immediate containing directory as the base name.
    """
    supported_extensions = {".jpg", ".jpeg", ".mov", ".mp4"}
    directory_path = Path(directory).expanduser().resolve()

    if not directory_path.is_dir():
        raise ValueError(f"Not a directory: {directory_path}")

    valid_files = (
        path
        for path in directory_path.rglob("*")
        if path.is_file() and path.suffix.lower() in supported_extensions
    )

    with ThreadPoolExecutor() as executor:
        for file, metadata_date in executor.map(get_metadata_date, valid_files):
            dt_str = metadata_date.strftime("%Y%m%d_%H%M%S")

            # Immediate containing directory, not the root directory passed in.
            dirname = file.parent.name

            if m := re.match(
                r"((((\d{1,4}[\W_]?){3,6})?(\(\d+\)){0,1})\s*){0,1}(?P<actual_dirname>.+)\s*",
                dirname,
            ):
                dirname = m.group("actual_dirname")

            new_suffix = ".jpg" if file.suffix.lower() == ".jpeg" else file.suffix.lower()

            new_name = f"{dt_str} {dirname}{new_suffix}"
            new_path = file.with_name(new_name)

            counter = 0

            while new_path.exists() and new_path != file:
                counter += 1
                new_name = f"{dt_str} {dirname} ({counter}){new_suffix}"
                new_path = file.with_name(new_name)

            if new_path != file:
                print(
                    f"Renaming: "
                    f"{file.relative_to(directory_path)} -> "
                    f"{new_path.relative_to(directory_path)}"
                )

                if do_action:
                    file.rename(new_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory",
        type=Path,
        help="Directory containing the media files to process",
    )
    parser.add_argument(
        "--do",
        action="store_true",
        help="Actually rename files. Without this option, perform a dry run.",
    )

    args = parser.parse_args()

    rename_files_in_directory(args.directory, do_action=args.do)
    