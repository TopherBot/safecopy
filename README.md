# safecopy

**safecopy** is a minimal, zero‑dependency Python tool that copies a file from `SOURCE` to `DESTINATION` **safely**.

- ✅ Verifies that the source file exists and is readable.
- ✅ Skips the copy if the destination already exists **and** its content matches the source (idempotent behavior).
- ✅ Emits helpful error messages for permission problems, missing files, or I/O failures.
- ✅ Works as a drop‑in replacement for `cp` in simple scripts where you want explicit safety guarantees.

## Installation

```bash
# Clone the repo (or download the single file)
git clone https://github.com/youruser/safecopy.git
cd safecopy
# No dependencies – just run it with Python 3.8+
```

## Usage

```bash
python3 safecopy.py <source_path> <destination_path>
```

### Examples

```bash
# Copy a file – creates the destination if needed
python3 safecopy.py data/input.txt backup/input.txt

# Running the command again does nothing (idempotent)
python3 safecopy.py data/input.txt backup/input.txt
```

## How it works

1. **Pre‑checks** – The script ensures the source file exists and can be opened.
2. **Hash comparison** – If the destination exists, it computes SHA‑256 hashes of both files. If they match, the copy is skipped with a friendly message.
3. **Copy** – If the destination is missing or differs, the file is copied in binary mode using `shutil.copyfileobj` with a buffered loop for large files.
4. **Error handling** – All anticipated errors (FileNotFoundError, PermissionError, OSError) are caught and reported with a non‑zero exit code.

## License

This project is released under the MIT License – see the `LICENSE` file in the repository.
