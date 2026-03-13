# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CSV Merger is a single-file Python GUI application that merges two CSV files and labels rows by brand type ("Apple" vs "Non-Apple"). It uses Tkinter for the GUI and pandas for CSV processing.

All application logic lives in **`csvscript.py`** (~220 lines).

## Development Setup

```bash
pip install pandas pyinstaller
python csvscript.py  # Run directly for development
```

## Building Executables

```bash
pyinstaller --onefile --windowed --name "CSV Merger" csvscript.py
# Output: dist/CSV Merger (or dist/CSV Merger.exe on Windows)
```

CI builds via GitHub Actions on push to `main`, producing artifacts for Windows (x64), macOS (x64, arm64), and Linux (x64) using Python 3.13.

## Architecture

The app has no test suite — validation is manual.

**Core pipeline in `csvscript.py`:**

1. **`detect_encoding()`** — tries utf-8, latin-1, windows-1252, cp1252, iso-8859-1 in order
2. **`detect_delimiter()`** — counts `,` `;` `|` `\t` in first line, picks most frequent
3. **`read_csv_with_encoding_fallback()`** — 4-step fallback: detected encoding → latin-1 → windows-1252 → latin-1 with `on_bad_lines='skip'`
4. **`standardize_delimiter()`** — normalizes output to comma-separated regardless of input delimiter
5. **`get_writable_output_path()`** — tries input file dir → home/Documents → home/Desktop → cwd, checking write permissions at each step
6. **`merge_csvs()`** — orchestrates the merge: reads both files, appends a "Brand Type" column ("Non-Apple" for file 1, "Apple" for file 2), concatenates, writes `merged_output.csv`
7. **GUI** — Tkinter 600×280 centered window; `browse_file()` opens file dialog, `run_merge()` calls `merge_csvs()` and updates status label (blue = processing, green = success, red = error)

## Key Behaviors to Preserve

- The "Brand Type" column assignment is intentional: first file = "Non-Apple", second file = "Apple"
- Output filename is always `merged_output.csv`
- Manual delimiter override in the GUI takes precedence over auto-detection
- The multi-step write-path fallback is needed for environments with restricted permissions (e.g., Windows protected folders)
