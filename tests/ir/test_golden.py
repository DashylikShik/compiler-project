#!/usr/bin/env python3
"""Golden tests for IR generation - compares output with expected files"""

import os
import sys
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class IRGoldenTester:
    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.passed = 0
        self.failed = 0
    
    def run_tests(self):
        """Run all golden tests"""
        print("GOLDEN TESTS FOR IR GENERATION")
        print()
        
        # Define test cases
        test_cases = [
            ('expressions', 'arithmetic', 'fn main() -> int { return 2 + 3; }'),
            ('expressions', 'multiplication', 'fn main() -> int { return 2 * 3; }'),
            ('expressions', 'nested', 'fn main() -> int { return 2 + 3 * 4; }'),
            ('control_flow', 'if_statement', 'fn main() -> int { int x = 5; if (x > 0) { return 1; } else { return 0; } }'),
            ('control_flow', 'while_loop', 'fn main() -> int { int i = 0; while (i < 10) { i = i + 1; } return i; }'),
            ('functions', 'call', 'fn add(int a, int b) -> int { return a + b; } fn main() -> int { return add(5, 3); }'),
            ('functions', 'multiple', 'fn one()->int{return 1;}fn two()->int{return 2;}fn three()->int{return 3;}'),
        ]
        
        for category, test_name, source in test_cases:
            self.run_single_test(category, test_name, source)
        
        print()
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
        
        if self.failed == 0:
            print(" ALL GOLDEN TESTS PASSED!")
        else:
            print(" SOME GOLDEN TESTS FAILED")
        
        return self.failed == 0
    
    def run_single_test(self, category, test_name, source):
        """Run single test and compare with expected"""
        expected_dir = os.path.join(self.base_dir, 'generation', category, 'expected')
        os.makedirs(expected_dir, exist_ok=True)
        
        expected_file = os.path.join(expected_dir, f"{test_name}.expected")
        
        # Create temp source file
        temp_file = os.path.join(self.base_dir, 'temp_test.src')
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(source)
        
        # Run compiler
        result = subprocess.run(
            ['python', 'src/main.py', 'ir', temp_file],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(self.base_dir))
        )
        
        # Extract IR output (skip headers)
        output_lines = []
        for line in result.stdout.split('\n'):
            if line.strip() and not line.startswith('#') and not line.startswith('=') and not line.startswith('-'):
                if 'func' in line or 'entry' in line or 'return' in line or '=' in line or 'jump' in line:
                    output_lines.append(line.rstrip())
        
        actual_output = '\n'.join(output_lines)
        
        # Clean up
        os.remove(temp_file)
        
        # Check or create expected file
        if os.path.exists(expected_file):
            with open(expected_file, 'r', encoding='utf-8') as f:
                expected_output = f.read().strip()
            
            if actual_output == expected_output:
                print(f"   {category}/{test_name}")
                self.passed += 1
            else:
                print(f"   {category}/{test_name}")
                self.failed += 1
        else:
            # Create expected file
            with open(expected_file, 'w', encoding='utf-8') as f:
                f.write(actual_output)
            print(f"   Created expected for {category}/{test_name}")
            self.passed += 1


def main():
    tester = IRGoldenTester()
    success = tester.run_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()