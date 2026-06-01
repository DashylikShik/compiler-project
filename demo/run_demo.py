#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT / "demo"

DEMOS = [
    {
        "name": "arrays_demo",
        "src": DEMO_DIR / "arrays_demo.src",
        "expected": 10,
        "optimize": False,
        "libs": [],
    },
    {
        "name": "external_demo",
        "src": DEMO_DIR / "external_demo.src",
        "expected": 5,
        "optimize": False,
        "libs": [],
    },
    {
        "name": "optimization_demo",
        "src": DEMO_DIR / "optimization_demo.src",
        "expected": 10,
        "optimize": True,
        "libs": [],
    },
]


def run(cmd, cwd=ROOT):
    print("$ " + " ".join(str(x) for x in cmd))
    return subprocess.run(cmd, cwd=cwd, check=False)


def build_and_run_demo(demo):
    name = demo["name"]
    src = demo["src"]
    asm = src.with_suffix(".asm")
    obj = ROOT / f"{name}.o"
    exe = ROOT / name

    print(f"DEMO: {name}")
    print(f"SOURCE: {src.relative_to(ROOT)}")

    if not src.exists():
        print(f"SKIP: файл не найден: {src.relative_to(ROOT)}")
        return False

    check = run(["python3", "src/main.py", "check", str(src.relative_to(ROOT))])
    if check.returncode != 0:
        print("RESULT: CHECK FAILED")
        return False

    compile_cmd = ["python3", "src/main.py", "compile", str(src.relative_to(ROOT))]
    if demo["optimize"]:
        compile_cmd += ["--optimize", "--verbose"]

    comp = run(compile_cmd)
    if comp.returncode != 0:
        print("RESULT: COMPILE FAILED")
        return False

    nasm = run(["nasm", "-f", "elf64", str(asm.relative_to(ROOT)), "-o", str(obj)])
    if nasm.returncode != 0:
        print("RESULT: NASM FAILED")
        return False

    gcc_cmd = ["gcc", "-no-pie", str(obj)]
    gcc_cmd += demo.get("libs", [])
    gcc_cmd += ["-o", str(exe)]

    gcc = run(gcc_cmd)
    if gcc.returncode != 0:
        print("RESULT: GCC FAILED")
        return False

    result = run([str(exe)])
    print(f"RETURN CODE: {result.returncode}")

    expected = demo["expected"]
    if result.returncode == expected:
        print("RESULT: OK")
        return True

    print(f"RESULT: FAIL, expected {expected}, got {result.returncode}")
    return False


def main():
    print("FINAL DEMO RUNNER")

    passed = 0
    failed = 0

    for demo in DEMOS:
        if build_and_run_demo(demo):
            passed += 1
        else:
            failed += 1

    print("DEMO SUMMARY")
    print(f"PASSED: {passed}")
    print(f"FAILED: {failed}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())