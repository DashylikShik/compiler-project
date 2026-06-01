#!/usr/bin/env python3
"""Единый тестовый раннер Sprint 8.

Раннер не заменяет старые тесты. Он запускает существующие runner/golden/unit тесты
и сохраняет общий JSON-отчёт в tests/final_reports/.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "tests" / "final_reports"


@dataclass
class TestResult:
    name: str
    command: list[str]
    returncode: int | None
    status: str
    stdout_tail: str = ""
    stderr_tail: str = ""
    note: str = ""


def tail(text: str, limit: int = 2500) -> str:
    text = text or ""
    return text[-limit:]


def run_cmd(name: str, command: list[str], *, allow_skip: bool = False, note: str = "") -> TestResult:
    print(f"{name}")
    print("$ " + " ".join(command))
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
    except FileNotFoundError as exc:
        status = "SKIP" if allow_skip else "FAIL"
        print(f"{status}: {exc}")
        return TestResult(name, command, None, status, note=str(exc))

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)

    status = "PASS" if result.returncode == 0 else "FAIL"
    print(f"RESULT: {status}")
    return TestResult(name, command, result.returncode, status, tail(result.stdout), tail(result.stderr), note)


def run_expect_failure(name: str, command: list[str], expected_markers: list[str]) -> TestResult:
    print(f"{name}")
    print("$ " + " ".join(command))
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    combined = (result.stdout or "") + "\n" + (result.stderr or "")
    print(combined)
    ok = result.returncode != 0 and any(marker.lower() in combined.lower() for marker in expected_markers)
    status = "PASS" if ok else "FAIL"
    print(f"RESULT: {status}")
    return TestResult(name, command, result.returncode, status, tail(result.stdout), tail(result.stderr), "expected failure test")


def main() -> int:
    py = sys.executable
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results: list[TestResult] = []

    # Sprint 1
    results.append(run_cmd("Sprint 1: lexer golden tests", [py, "tests/test_runner.py"]))

    # Sprint 2
    results.append(run_cmd("Sprint 2: parser pytest tests", [py, "-m", "pytest", "tests/parser", "-v"]))

    # Sprint 3
    results.append(run_cmd("Sprint 3: semantic unit tests", [py, "-m", "unittest", "tests.test_semantic", "-v"]))

    # Sprint 4
    results.append(run_cmd("Sprint 4: IR unit tests", [py, "tests/ir/test_runner.py"]))
    results.append(run_cmd("Sprint 4: IR golden tests", [py, "tests/ir/test_golden.py"]))

    # Sprint 5
    results.append(run_cmd("Sprint 5: x86 codegen tests", [py, "tests/codegen/test_runner.py"]))

    # Sprint 6
    results.append(run_cmd("Sprint 6: control-flow tests", [py, "tests/control_flow/test_runner.py"]))
    results.append(run_cmd("Sprint 6: control-flow golden tests", [py, "tests/control_flow/test_golden.py"]))

    # Sprint 7 unit/integration
    results.append(run_cmd(
        "Sprint 7: optimization unit tests",
        ["bash", "-c", f"PYTHONPATH=src {py} -m unittest tests.optimization.test_constant_folding -v"]
    ))

    if (ROOT / "run_valid_tests.py").exists():
        results.append(run_cmd("Sprint 7: arrays/external/optimization integration", [py, "run_valid_tests.py"]))
    else:
        results.append(TestResult("Sprint 7 integration", [py, "run_valid_tests.py"], None, "SKIP", note="run_valid_tests.py not found"))

    results.append(run_expect_failure(
        "Sprint 7 invalid: array out of bounds",
        [py, "src/main.py", "check", "tests/array/invalid/01_out_of_bounds.src"],
        ["out of bounds", "array index", "ошибки семантического анализа"],
    ))
    results.append(run_expect_failure(
        "Sprint 7 invalid: wrong extern args",
        [py, "src/main.py", "check", "tests/external/invalid/01_wrong_args.src"],
        ["expects at least", "argument", "ошибки семантического анализа"],
    ))

    results.append(run_cmd("Sprint 7: demo", [py, "demo/run_demo.py"]))

    # Sprint 8 smoke tests
    if (ROOT / "mycc.py").exists():
        results.append(run_cmd("Sprint 8: CLI --help", [py, "mycc.py", "--help"]))
        results.append(run_cmd("Sprint 8: CLI --version", [py, "mycc.py", "--version"]))
        if (ROOT / "demo" / "optimization_demo.src").exists():
            results.append(run_cmd("Sprint 8: CLI assembly only", [py, "mycc.py", "-S", "demo/optimization_demo.src", "-o", "tests/final_reports/optimization_demo.asm"]))
    else:
        results.append(TestResult("Sprint 8 CLI", [py, "mycc.py"], None, "SKIP", note="mycc.py not found"))

    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    skipped = sum(1 for r in results if r.status == "SKIP")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "project_root": str(ROOT),
        "summary": {"passed": passed, "failed": failed, "skipped": skipped, "total": len(results)},
        "results": [asdict(r) for r in results],
    }
    report_file = REPORT_DIR / "last_run.json"
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print("ИТОГОВЫЙ ОТЧЁТ")
    print(f"PASS: {passed}")
    print(f"FAIL: {failed}")
    print(f"SKIP: {skipped}")
    print(f"TOTAL: {len(results)}")
    print(f"JSON report: {report_file}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
