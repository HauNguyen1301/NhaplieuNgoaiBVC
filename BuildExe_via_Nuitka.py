"""
BuildExe_via_Nuitka.py
Helper script to compile the NhaplieuNgoaiBVC application into a single EXE using Nuitka.

Requirements:
1. Python 3.8+ (same major/minor as the project runtime).
2. Nuitka and its dependencies. Install with:
   pip install nuitka zstandard

Usage (PowerShell/CMD):
    python BuildExe_via_Nuitka.py

Options:
    --output NAME  Specify output exe name (default: NhapLieuNgoaiBVC-0.1.1.exe).
    --noconsole    Build without a console window (default for this GUI app).

This script wraps the Nuitka CLI, adding sensible defaults for this project,
such as including the tkinter plugin, required modules, and the SQLite database.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

from app_version import __version__ as APP_VERSION

PROJECT_ROOT = Path(__file__).resolve().parent
ENTRY_SCRIPT = PROJECT_ROOT / "main.py"
DEFAULT_EXE_NAME = f"NhapLieuNgoaiBVC-v{APP_VERSION}.exe"


def run(cmd: List[str]):
    """Run a shell command, forwarding output. Exit on failure."""
    print("Executing:", " ".join(map(str, cmd)))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}")
        sys.exit(exc.returncode)
    except FileNotFoundError:
        print(f"Error: Command '{cmd[0]}' not found. Is Python/Nuitka in your PATH?")
        sys.exit(1)


def main():
    """Compile the app into a single-file EXE using Nuitka with sensible defaults."""

    parser = argparse.ArgumentParser(description="Build NhapLieuNgoaiBVC with Nuitka")
    parser.add_argument("--output", default=DEFAULT_EXE_NAME,
                        help=f"Executable file name (default: {DEFAULT_EXE_NAME})")
    parser.add_argument("--console", action="store_true", help="Show the console window (for debugging)")
    args = parser.parse_args()

    output_name = args.output

    # Clean previous build directories to avoid stale files
    for path in PROJECT_ROOT.iterdir():
        if path.is_dir() and (path.name == "build" or path.name.endswith(".build") or path.name.endswith(".dist")):
            print(f"Removing previous build directory: {path}")
            shutil.rmtree(path, ignore_errors=True)

    nuitka_opts = [
        "-m",
        "nuitka",
        str(ENTRY_SCRIPT),
        "--onefile",
        "--enable-plugin=tk-inter",
        "--include-module=ttkbootstrap",
        "--include-module=requests",
        "--include-module=packaging",
        "--include-module=webbrowser",
        "--include-module=sqlite3",
        # Include the entire 'database' folder, which contains the .db file
        f"--include-data-dir={PROJECT_ROOT / 'database'}=database",
        # Include the .env file for database credentials
        f"--include-data-file={PROJECT_ROOT / '.env'}=.env",
        # Explicitly include the main application package
        "--include-module=chuc_nang_chinh",
        f"--output-filename={output_name}",
        "--nofollow-import-to=tests,__pycache__",
        "--no-pyi-file",
        "--python-flag=no_site",
    ]

    # By default, disable the console for a GUI application
    if not args.console:
        nuitka_opts.append("--windows-disable-console")

    cmd = [sys.executable] + nuitka_opts
    run(cmd)

    # --- Post-build cleanup ---

    # Move the generated exe into our own 'release' folder
    exe_src = PROJECT_ROOT / output_name
    release_dir = PROJECT_ROOT / "release"
    release_dir.mkdir(exist_ok=True)
    dest_exe = release_dir / output_name

    if dest_exe.exists():
        print(f"Removing old executable at {dest_exe}")
        dest_exe.unlink()

    if exe_src.exists():
        print(f"Moving '{exe_src.name}' to '{release_dir.name}' directory...")
        shutil.move(str(exe_src), dest_exe)
        print(f"Moved {output_name} -> {dest_exe}")
    else:
        print(f"Error: Expected executable '{output_name}' not found in project root after build.")


    # Clean up any remaining build artifacts
    for path in PROJECT_ROOT.iterdir():
        if path.is_dir() and (path.name == "build" or path.name.endswith(".build") or path.name.endswith(".dist")):
            print(f"Cleaning final build artifact: {path}")
            shutil.rmtree(path, ignore_errors=True)

    print(f"\n✅ Build completed! Find your executable in the '{release_dir.name}' directory. ✅")


if __name__ == "__main__":
    main()
