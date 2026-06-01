#!/usr/bin/env python3
"""Golden tests for Sprint 6 - Control Flow & Logical Operators"""

import os
import sys
import subprocess
import difflib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class GoldenTester:
    def __init__(self):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.passed = 0
        self.failed = 0
        self.generated = 0
    
    def run_test(self, test_name, src_file, expected_file, category):
        """Run single golden test"""
        print(f"\n {category}/{test_name}")
        
        # Компилируем в ассемблер
        result = subprocess.run(
            ['python3', 'src/main.py', 'compile', src_file],
            capture_output=True, text=True,
            cwd=self.project_root
        )
        
        if result.returncode != 0:
            print(f"   Compilation failed: {result.stderr}")
            self.failed += 1
            return False
        
        # Читаем сгенерированный ассемблер
        asm_file = src_file.replace('.src', '.asm')
        if not os.path.exists(asm_file):
            print(f"   Assembly file not created")
            self.failed += 1
            return False
        
        with open(asm_file, 'r', encoding='utf-8') as f:
            actual_output = f.read()
        
        # Сохраняем output
        output_dir = os.path.join(self.project_root, 'tests', 'control_flow', 'output')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{test_name}.output")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(actual_output)
        
        # Сравниваем с expected
        if os.path.exists(expected_file):
            with open(expected_file, 'r', encoding='utf-8') as f:
                expected_output = f.read()
            
            if actual_output == expected_output:
                print(f"   {test_name} - PASSED (matches expected)")
                self.passed += 1
                return True
            else:
                # Показываем diff
                diff = difflib.unified_diff(
                    expected_output.splitlines(),
                    actual_output.splitlines(),
                    fromfile='expected',
                    tofile='actual',
                    lineterm=''
                )
                print(f"   {test_name} - FAILED (does not match expected)")
                print("\n  Diff:")
                for line in list(diff)[:10]:
                    print(f"    {line}")
                self.failed += 1
                return False
        else:
            # Создаем expected файл
            os.makedirs(os.path.dirname(expected_file), exist_ok=True)
            with open(expected_file, 'w', encoding='utf-8') as f:
                f.write(actual_output)
            print(f"   {test_name} - GENERATED expected file")
            self.generated += 1
            self.passed += 1
            return True
    
    def run_all_tests(self):
        print()
        
        tests = [
            ("if_else", "conditionals", "if_else.src"),
            ("while_loop", "loops", "while_loop.src"),
            ("for_loop", "loops", "for_loop.src"),
            ("short_circuit_and", "logical_ops", "short_circuit_and.src"),
            ("precedence", "complex_expressions", "precedence.src"),
        ]
        
        for test_name, category, src_name in tests:
            src_file = os.path.join(
                self.project_root, 'tests', 'control_flow', 'valid', 
                category, src_name
            )
            expected_file = os.path.join(
                self.project_root, 'tests', 'control_flow', 'valid',
                category, 'expected', f"{test_name}.expected"
            )
            
            if os.path.exists(src_file):
                self.run_test(test_name, src_file, expected_file, category)
            else:
                print(f"\n Test file not found: {src_file}")
        

        print(f"   Passed: {self.passed}")
        print(f"   Failed: {self.failed}")
        print(f"   Generated: {self.generated}")
        
        if self.failed == 0:
            print("\n ALL GOLDEN TESTS PASSED!")
            return 0
        else:
            print(f"\n {self.failed} tests failed")
            return 1


if __name__ == "__main__":
    tester = GoldenTester()
    sys.exit(tester.run_all_tests())