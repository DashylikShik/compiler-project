#!/usr/bin/env python3
"""CLI wrapper for MiniCompiler Sprint 8.

This file does not replace src/main.py. It provides a Unix-like command line
interface around the existing compiler pipeline.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

VERSION = "MiniCompiler mycc 1.0.0"
TARGET = "x86_64-linux-gnu"


def run(cmd: list[str], *, verbose: bool = False) -> int:
    if verbose:
        print("$ " + " ".join(cmd))
    return subprocess.run(cmd).returncode


def run_capture(cmd: list[str], *, verbose: bool = False) -> subprocess.CompletedProcess:
    if verbose:
        print("$ " + " ".join(cmd))
    return subprocess.run(cmd, text=True, capture_output=True)


def find_tool(name: str) -> bool:
    return shutil.which(name) is not None


def compile_to_asm(src: Path, asm: Path, optimize: bool, verbose: bool) -> int:
    cmd = [sys.executable, "src/main.py", "compile", str(src), "--output", str(asm)]
    if optimize:
        cmd.append("--optimize")
    if verbose:
        cmd.append("--verbose")
    return run(cmd, verbose=verbose)


def assemble(asm: Path, obj: Path, verbose: bool) -> int:
    if not find_tool("nasm"):
        print("error: nasm не найден. Установите: sudo apt install nasm")
        return 1
    return run(["nasm", "-f", "elf64", str(asm), "-o", str(obj)], verbose=verbose)


def link(objects: list[Path], output: Path, libs: list[str], lib_dirs: list[str], verbose: bool) -> int:
    if not find_tool("gcc"):
        print("error: gcc не найден. Установите: sudo apt install gcc")
        return 1
    cmd = ["gcc", "-no-pie"] + [str(o) for o in objects]
    for lib_dir in lib_dirs:
        cmd.append(f"-L{lib_dir}")
    for lib in libs:
        if lib.startswith("-l"):
            cmd.append(lib)
        else:
            cmd.append(f"-l{lib}")
    cmd += ["-o", str(output)]
    return run(cmd, verbose=verbose)


def preprocess_only(files: list[Path]) -> int:
    for src in files:
        print(src.read_text(encoding="utf-8"))
    return 0


def show_ast(src: Path, output: str | None, verbose: bool) -> int:
    cmd = [sys.executable, "src/main.py", "parse", "--format", "text"]
    if output:
        cmd += ["--output", output]
    cmd.append(str(src))
    return run(cmd, verbose=verbose)


def show_ir(src: Path, output: str | None, verbose: bool, optimize: bool) -> int:
    cmd = [sys.executable, "src/main.py", "ir"]
    if verbose:
        cmd.append("--verbose")
    if output:
        cmd += ["--output", output]
    cmd.append(str(src))
    # Existing src/main.py does not optimize in the IR command; optimization is
    # available in compile mode. We keep --ir as inspection mode.
    return run(cmd, verbose=verbose)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mycc",
        description="MiniCompiler command line interface",
    )
    parser.add_argument("files", nargs="*", help="source .src files")
    parser.add_argument("-o", "--output", help="output file")
    parser.add_argument("-S", action="store_true", help="generate assembly only")
    parser.add_argument("-c", action="store_true", help="compile to object file only")
    parser.add_argument("-E", action="store_true", help="preprocess only")
    parser.add_argument("--ast", action="store_true", help="print AST")
    parser.add_argument("--ir", action="store_true", help="print IR")
    parser.add_argument("--optimize", action="store_true", help="enable optimizations")
    parser.add_argument("-O", dest="opt_level", nargs="?", const="1", help="optimization level 0-3")
    parser.add_argument("--target", default=TARGET, help="target architecture")
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
    parser.add_argument("--version", action="store_true", help="show version")
    parser.add_argument("-l", dest="libs", action="append", default=[], help="link with library")
    parser.add_argument("-L", dest="lib_dirs", action="append", default=[], help="add library directory")
    parser.add_argument("-I", dest="include_dirs", action="append", default=[], help="add include directory (reserved)")
    parser.add_argument("--color", default="auto", choices=["auto", "always", "never"], help="color mode")

    args = parser.parse_args(argv)

    if args.version:
        print(VERSION)
        print(f"Target: {args.target}")
        return 0

    if not args.files:
        parser.print_help()
        return 1

    sources = [Path(f) for f in args.files]
    for src in sources:
        if not src.exists():
            print(f"error: файл не найден: {src}")
            return 1

    optimize = args.optimize or (args.opt_level is not None and args.opt_level != "0")

    if args.E:
        return preprocess_only(sources)

    if args.ast:
        if len(sources) != 1:
            print("error: --ast поддерживает один файл за запуск")
            return 1
        return show_ast(sources[0], args.output, args.verbose)

    if args.ir:
        if len(sources) != 1:
            print("error: --ir поддерживает один файл за запуск")
            return 1
        return show_ir(sources[0], args.output, args.verbose, optimize)

    objects: list[Path] = []

    for idx, src in enumerate(sources):
        if args.S and len(sources) == 1 and args.output:
            asm = Path(args.output)
        else:
            asm = src.with_suffix(".asm")

        rc = compile_to_asm(src, asm, optimize, args.verbose)
        if rc != 0:
            return rc

        if args.S:
            continue

        if args.c and len(sources) == 1 and args.output:
            obj = Path(args.output)
        else:
            obj = Path(src.stem + ".o")

        rc = assemble(asm, obj, args.verbose)
        if rc != 0:
            return rc
        objects.append(obj)

    if args.S:
        return 0

    if args.c:
        return 0

    output = Path(args.output) if args.output else Path(sources[0].stem)
    return link(objects, output, args.libs, args.lib_dirs, args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
