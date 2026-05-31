#!/usr/bin/env python3
import subprocess
from pathlib import Path

ARRAY_VALID = sorted([
    "tests/array/valid/01_declaration.src",
    "tests/array/valid/02_initialized.src",
    "tests/array/valid/03_access.src",
    "tests/array/valid/04_multidim.src",
])

EXTERNAL_VALID = sorted([
    "tests/external/valid/01_printf.src",
    "tests/external/valid/02_malloc.src",
    "tests/external/valid/03_math.src",
    "tests/external/valid/04_string.src"
])

OPT_VALID = sorted([
    "tests/optimization/valid/01_folding.src",
    "tests/optimization/valid/02_propagation.src",
    "tests/optimization/valid/03_dce.src",
    "tests/optimization/valid/04_compare.src",
    "tests/optimization/valid/05_logic.src",
    "tests/optimization/valid/06_mixed.src"
])

def run(cmd):
    print("$ " + " ".join(cmd))
    return subprocess.run(cmd, check=False)

# Глобальный словарь для хранения ASM без оптимизации
NO_OPT_ASM = {}

def build_and_run(src_name, optimize=False):
    src = Path(src_name)
    suffix = "_opt" if optimize else ""
    asm = src.with_suffix(".asm")
    obj = Path(src.stem + suffix + ".o")
    exe = Path(src.stem + suffix)

    print(f"TEST: {src}")
    print("MODE:", "OPTIMIZED" if optimize else "NORMAL")

    # 1. Семантика
    run(["python3", "src/main.py", "check", str(src)])

    # 2. Компиляция
    compile_cmd = ["python3", "src/main.py", "compile", str(src)]
    if optimize:
        compile_cmd += ["--optimize", "--verbose"]

    result = run(compile_cmd)
    if result.returncode != 0:
        print(f"COMPILE FAILED: {src}")
        return None

    # 3. Сохраняем ASM для diff
    if "optimization" in str(src):
        if not optimize:
            no_opt_asm = src.with_name(f"{src.stem}_no_opt.asm")
            NO_OPT_ASM[src.stem] = no_opt_asm
            run(["cp", str(asm), str(no_opt_asm)])
        else:
            opt_asm = src.with_name(f"{src.stem}_opt.asm")
            run(["cp", str(asm), str(opt_asm)])
            # делаем diff с сохранённой версией
            no_opt_asm = NO_OPT_ASM.get(src.stem)
            if no_opt_asm and no_opt_asm.exists():
                run(["diff", "-u", str(no_opt_asm), str(opt_asm)])

    # 4. NASM
    result = run(["nasm", "-f", "elf64", str(asm), "-o", str(obj)])
    if result.returncode != 0:
        print(f"NASM FAILED: {asm}")
        return None

    # 5. GCC
    gcc_cmd = ["gcc", "-no-pie", str(obj)]
    if src.name == "03_math.src":
        gcc_cmd.append("-lm")
    gcc_cmd += ["-o", str(exe)]
    result = run(gcc_cmd)
    if result.returncode != 0:
        print(f"GCC FAILED: {obj}")
        return None

    # 6. Run binary
    result = run([f"./{exe}"])
    print(f"RETURN CODE: {result.returncode}")
    return result.returncode

def main():
    print("\n  ARRAY VALID  ")
    for test in ARRAY_VALID:
        build_and_run(test, optimize=False)

    print("\n  EXTERNAL VALID  ")
    for test in EXTERNAL_VALID:
        build_and_run(test, optimize=False)

    print("\n  OPTIMIZATION TESTS: NORMAL vs OPTIMIZED  ")
    for test in OPT_VALID:
        normal = build_and_run(test, optimize=False)
        optimized = build_and_run(test, optimize=True)
        print("\nCOMPARE:", test)
        print(f"WITHOUT OPTIMIZE: {normal}")
        print(f"WITH OPTIMIZE:    {optimized}")
        if normal == optimized:
            print("RESULT: OK")
        else:
            print("RESULT: MISMATCH")

if __name__ == "__main__":
    main()