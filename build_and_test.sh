#!/usr/bin/env bash
echo " MiniCompiler Full Validation"

echo
echo "[1/10] Lexer"
python3 tests/test_runner.py

echo
echo "[2/10] Parser"
python3 -m pytest tests/parser -v

echo
echo "[3/10] Semantic"
python3 -m unittest tests.test_semantic -v

echo
echo "[4/10] IR"
python3 tests/ir/test_runner.py
python3 tests/ir/test_golden.py

echo
echo "[5/10] Code Generation"
python3 tests/codegen/test_runner.py

echo
echo "[6/10] Control Flow"
python3 tests/control_flow/test_runner.py
python3 tests/control_flow/test_golden.py

echo
echo "[7/10] Optimization"
python3 -m unittest tests.optimization.test_constant_folding -v

echo
echo "[8/10] Sprint 7"
python3 run_valid_tests.py

echo
echo "[9/10] Demo"
python3 demo/run_demo.py

echo
echo "[10/10] CLI"
python3 mycc.py --help
python3 mycc.py --version