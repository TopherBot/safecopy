#!/usr/bin/env python3
"""safecopy – a tiny, idempotent file copy utility with robust error handling.

Usage:
    python3 safecopy.py <source_path> <destination_path>

The script will:
  * Verify that <source_path> exists and is readable.
  * If <destination_path> exists and its content matches the source, skip copying.
  * Otherwise, copy the file in binary mode with a buffered stream.
  * Emit clear error messages and exit with a non‑zero code on failure.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

BUF_SIZE = 1024 * 1024  # 1 MiB


def compute_sha256(file_path: Path) -> str:
    """Return the SHA‑256 hex digest of *file_path*.
    Handles large files efficiently by streaming.
    """
    h = hashlib.sha256()
    try:
        with file_path.open('rb') as f:
            for chunk in iter(lambda: f.read(BUF_SIZE), b''):
                h.update(chunk)
    except PermissionError as e:
        raise PermissionError(f"Cannot read '{file_path}': {e.strerror}") from e
    except OSError as e:
        raise OSError(f"I/O error while reading '{file_path}': {e.strerror}") from e
    return h.hexdigest()


def copy_file(src: Path, dst: Path) -> None:
    """Copy *src* to *dst* using a buffered stream.
    Guarantees the destination directory exists.
    """
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with src.open('rb') as src_f, dst.open('wb') as dst_f:
            shutil.copyfileobj(src_f, dst_f, length=BUF_SIZE)
    except PermissionError as e:
        raise PermissionError(f"Permission denied during copy: {e.strerror}") from e
    except OSError as e:
        raise OSError(f"I/O error during copy: {e.strerror}") from e


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("Usage: python3 safecopy.py <source_path> <destination_path>", file=sys.stderr)
        return 2

    src_path = Path(argv[1]).resolve()
    dst_path = Path(argv[2]).resolve()

    # Pre‑check: source must exist and be a file.
    if not src_path.is_file():
        print(f"Error: source file '{src_path}' does not exist or is not a regular file.", file=sys.stderr)
        return 1

    try:
        src_hash = compute_sha256(src_path)
    except Exception as e:
        print(f"Error computing hash of source: {e}", file=sys.stderr)
        return 1

    # Destination handling
    if dst_path.exists():
        if not dst_path.is_file():
            print(f"Error: destination '{dst_path}' exists and is not a regular file.", file=sys.stderr)
            return 1
        try:
            dst_hash = compute_sha256(dst_path)
        except Exception as e:
            print(f"Error computing hash of destination: {e}", file=sys.stderr)
            return 1
        if src_hash == dst_hash:
            print(f"Skipped: destination '{dst_path}' already matches source.")
            return 0
        else:
            print(f"Info: destination exists but differs – overwriting.")
            # Overwrite will happen below.
    else:
        print(f"Info: destination '{dst_path}' does not exist – creating.")

    try:
        copy_file(src_path, dst_path)
        # Verify copy succeeded by recomputing hash (optional safety net).
        if compute_sha256(dst_path) != src_hash:
            print("Error: post‑copy verification failed – hashes do not match.", file=sys.stderr)
            return 1
        print(f"Successfully copied '{src_path}' → '{dst_path}'.")
    except Exception as e:
        print(f"Error during copy: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
