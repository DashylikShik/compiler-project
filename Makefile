PYTHON ?= python3

.PHONY: help test-all test-lexer test-parser test-semantic test-ir test-codegen test-control-flow test-optimization test-sprint7 demo clean

help:
	@echo "MiniCompiler Makefile"
	@echo "  make test-all          - запустить все тесты проекта"
	@echo "  make test-lexer        - тесты лексера"
	@echo "  make test-parser       - тесты парсера"
	@echo "  make test-semantic     - тесты семантики"
	@echo "  make test-ir           - тесты IR"
	@echo "  make test-codegen      - тесты codegen"
	@echo "  make test-control-flow - тесты control-flow"
	@echo "  make test-optimization - тесты оптимизаций"
	@echo "  make test-sprint7      - интеграционные тесты Sprint 7"
	@echo "  make demo              - запустить demo"
	@echo "  make clean             - удалить временные файлы сборки"

test-all:
	$(PYTHON) tests/all_tests.py

test-lexer:
	$(PYTHON) tests/test_runner.py

test-parser:
	$(PYTHON) -m pytest tests/parser -v

test-semantic:
	$(PYTHON) -m unittest tests.test_semantic -v

test-ir:
	$(PYTHON) tests/ir/test_runner.py
	$(PYTHON) tests/ir/test_golden.py

test-codegen:
	$(PYTHON) tests/codegen/test_runner.py

test-control-flow:
	$(PYTHON) tests/control_flow/test_runner.py
	$(PYTHON) tests/control_flow/test_golden.py

test-optimization:
	$(PYTHON) -m unittest tests.optimization.test_constant_folding -v

test-sprint7:
	$(PYTHON) run_valid_tests.py
	$(PYTHON) src/main.py check tests/array/invalid/01_out_of_bounds.src || true
	$(PYTHON) src/main.py check tests/external/invalid/01_wrong_args.src || true

demo:
	python3 demo/run_demo.py

clean:
	find . -name "*.o" -delete
	find . -name "*.asm" -not -path "./tests/*" -not -path "./demo/*" -delete
	find . -maxdepth 1 -type f -perm -111 -not -name "mycc" -delete || true
	rm -rf tests/final_reports .pytest_cache __pycache__
