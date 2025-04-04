import asyncio
import argparse
import logging
from pathlib import Path
import shutil

# Logger setup
logger = logging.getLogger("file-sort-logger")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter("%(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def parse_arguments():
    parser = argparse.ArgumentParser(description="Asynchronous file sorting by extension")
    parser.add_argument("source", type=str, help="Path to the source folder")
    parser.add_argument("output", type=str, help="Path to the output folder")
    return parser.parse_args()

async def copy_file(file_path: Path, output_folder: Path):
    try:
        extension = file_path.suffix.lstrip(".") or "unknown"
        target_folder = output_folder / extension
        target_folder.mkdir(parents=True, exist_ok=True)

        target_path = target_folder / file_path.name
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, shutil.copy2, file_path, target_path)
        logger.info(f"Copied: {file_path} -> {target_path}")
    except Exception as e:
        logger.error(f"Error copying {file_path}: {e}")

async def read_folder(source_folder: Path, output_folder: Path):
    tasks = []
    for file_path in source_folder.rglob("*"):
        if file_path.is_file():
            tasks.append(copy_file(file_path, output_folder))
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    args = parse_arguments()

    source_path = Path(args.source)
    output_path = Path(args.output)

    if not source_path.exists() or not source_path.is_dir():
        logger.error(f"Source path '{source_path}' does not exist or is not a directory.")
        exit(1)

    asyncio.run(read_folder(source_path, output_path))
