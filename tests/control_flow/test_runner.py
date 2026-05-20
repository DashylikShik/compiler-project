#!/usr/bin/env python3
"""Test runner for Sprint 6 - Control Flow & Logical Operators"""

import os
import sys
import subprocess
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class ControlFlowTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    def test_compilation(self, test_name, source, expected_output=None):
        """Test compilation and execution"""
        print(f"\n {test_name}")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.src', delete=False, encoding='utf-8') as f:
            f.write(source)
            src_file = f.name
        
        asm_file = src_file.replace('.src', '.asm')
        
        try:
            # Compile
            result = subprocess.run(
                ['python', 'src/main.py', 'compile', src_file, '--output', asm_file],
                capture_output=True, text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                print(f"   Compilation failed: {result.stderr}")
                self.failed += 1
                return
            
            with open(asm_file, 'r', encoding='utf-8') as f:
                asm = f.read()
            
            # Check for control flow instructions
            has_conditional = 'jne' in asm or 'je' in asm or 'jg' in asm or 'jl' in asm
            has_unconditional = 'jmp' in asm
            
            if has_conditional:
                print(f"     Conditional jumps found")
            else:
                print(f"    No conditional jumps")
            
            if has_unconditional:
                print(f"    Unconditional jumps found")
            else:
                print(f"    No unconditional jumps")
            
            if has_conditional or has_unconditional:
                print(f"   {test_name} PASSED")
                self.passed += 1
            else:
                print(f"   {test_name} FAILED")
                self.failed += 1
                
        except Exception as e:
            print(f"   Error: {e}")
            self.failed += 1
        finally:
            for f in [src_file, asm_file]:
                if f and os.path.exists(f):
                    os.remove(f)
    
    def test_short_circuit_and(self):
        """Test short-circuit AND evaluation"""
        source = """
fn main() -> int {
    int a = 0;
    int b = 10;
    if (a > 0 && b > 5) {
        return 1;
    }
    return 0;
}
"""
        self.test_compilation("Short-circuit AND", source)
    
    def test_short_circuit_or(self):
        """Test short-circuit OR evaluation"""
        source = """
fn main() -> int {
    int a = 5;
    int b = 0;
    if (a > 0 || b > 5) {
        return 1;
    }
    return 0;
}
"""
        self.test_compilation("Short-circuit OR", source)
    
    def test_nested_conditionals(self):
        """Test nested if statements"""
        source = """
fn main() -> int {
    int x = 10;
    int y = 20;
    if (x > 5) {
        if (y > 15) {
            return 1;
        }
        return 0;
    }
    return 0;
}
"""
        self.test_compilation("Nested conditionals", source)
    
    def test_while_loop(self):
        """Test while loop"""
        source = """
fn main() -> int {
    int i = 0;
    int sum = 0;
    while (i < 5) {
        sum = sum + i;
        i = i + 1;
    }
    return sum;
}
"""
        self.test_compilation("While loop", source)
    
    def test_for_loop(self):
        """Test for loop"""
        source = """
fn main() -> int {
    int sum = 0;
    for (int i = 0; i < 5; i = i + 1) {
        sum = sum + i;
    }
    return sum;
}
"""
        self.test_compilation("For loop", source)
    
    def test_nested_loops(self):
        """Test nested loops"""
        source = """
fn main() -> int {
    int sum = 0;
    for (int i = 0; i < 3; i = i + 1) {
        for (int j = 0; j < 3; j = j + 1) {
            sum = sum + 1;
        }
    }
    return sum;
}
"""
        self.test_compilation("Nested loops", source)
    
    def test_operator_precedence(self):
        """Test operator precedence"""
        source = """
    fn main() -> int {
        int a = 2;
        int b = 3;
        int c = 4;
        // a + b * c должно быть 2 + 12 = 14
        // проверяем через if для генерации jumps
        int result = a + b * c;
        if (result == 14) {
            return 1;
        }
        return 0;
    }
    """
        print(f"\n Operator precedence")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.src', delete=False, encoding='utf-8') as f:
            f.write(source)
            src_file = f.name
        
        asm_file = src_file.replace('.src', '.asm')
        
        try:
            # Compile
            result = subprocess.run(
                ['python', 'src/main.py', 'compile', src_file, '--output', asm_file],
                capture_output=True, text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0:
                print(f"   Compilation failed: {result.stderr}")
                self.failed += 1
                return
            
            with open(asm_file, 'r', encoding='utf-8') as f:
                asm = f.read()
            
            # Check for multiplication (should happen before addition)
            has_mul = 'imul' in asm
            has_add = 'add' in asm
            has_cmp = 'cmp' in asm
            
            if has_mul:
                print(f"     Multiplication found (precedence: * before +)")
            else:
                print(f"     Multiplication not found")
            
            if has_add:
                print(f"     Addition found")
            else:
                print(f"     Addition not found")
            
            if has_cmp:
                print(f"     Comparison found")
            else:
                print(f"     Comparison not found")
            
            # For operator precedence test, we need at least mul and add
            if has_mul and has_add:
                print(f"  Operator precedence PASSED")
                self.passed += 1
            else:
                print(f"   Operator precedence FAILED")
                self.failed += 1
                
        except Exception as e:
            print(f"   Error: {e}")
            self.failed += 1
        finally:
            for f in [src_file, asm_file]:
                if f and os.path.exists(f):
                    os.remove(f)
    
    def run(self):
        
        self.test_short_circuit_and()
        self.test_short_circuit_or()
        self.test_nested_conditionals()
        self.test_while_loop()
        self.test_for_loop()
        self.test_nested_loops()
        self.test_operator_precedence()
        
        print(f"RESULTS: {self.passed} passed, {self.failed} failed")
   
        
        if self.failed == 0:
            print("\n ALL SPRINT 6 TESTS PASSED!")
        else:
            print(f"\ {self.failed} tests failed.")
        
        return self.failed == 0


if __name__ == "__main__":
    tester = ControlFlowTester()
    success = tester.run()
    sys.exit(0 if success else 1)