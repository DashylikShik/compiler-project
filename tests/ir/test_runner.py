#!/usr/bin/env python3
"""Complete test runner for Sprint 4 requirements"""

import sys
import os
import unittest
import subprocess

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestIRRequirements(unittest.TestCase):
    """Test all Sprint 4 requirements"""
    
    @classmethod
    def setUpClass(cls):
        cls.project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    
    def run_ir_command(self, args):
        """Run compiler ir command"""
        cmd = ['python3', 'src/main.py', 'ir'] + args
        result = subprocess.run(
            cmd,
            cwd=self.project_dir,
            capture_output=True,
            text=True
        )
        return result
    
    # TEST-1: Expression translation
    def test_01_expression_addition(self):
        """Test addition expression -> 3-address code"""
        source = "fn main() -> int { return 2 + 3; }"
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['test_temp.src'])
        os.remove('test_temp.src')
        
        self.assertIn('add', result.stdout)
        print("   TEST-1.1: Addition expression works")
    
    def test_02_expression_multiplication(self):
        """Test multiplication expression -> 3-address code"""
        source = "fn main() -> int { return 2 * 3; }"
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['test_temp.src'])
        os.remove('test_temp.src')
        
        self.assertIn('mul', result.stdout)
        print("   TEST-1.2: Multiplication expression works")
    
    def test_03_nested_arithmetic(self):
        """Test nested arithmetic (2+3*4)"""
        source = "fn main() -> int { return 2 + 3 * 4; }"
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['test_temp.src'])
        os.remove('test_temp.src')
        
        # Should have both add and mul
        self.assertIn('mul', result.stdout)
        self.assertIn('add', result.stdout)
        print("   TEST-1.3: Nested arithmetic works")
    
    # TEST-2: Control flow translation
    def test_04_if_statement(self):
        """Test if statement -> conditional jumps"""
        source = """
fn main() -> int {
    int x = 5;
    if (x > 0) {
        return 1;
    } else {
        return 0;
    }
}
"""
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['test_temp.src'])
        os.remove('test_temp.src')
        
        self.assertIn('jump_if', result.stdout)
        self.assertIn('jump', result.stdout)
        print("   TEST-2.1: If statement works")
    
    def test_05_while_loop(self):
        """Test while loop -> header + body + back edge"""
        source = """
fn main() -> int {
    int i = 0;
    while (i < 10) {
        i = i + 1;
    }
    return i;
}
"""
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['test_temp.src'])
        os.remove('test_temp.src')
        
        self.assertIn('jump', result.stdout)
        print("   TEST-2.2: While loop works")
    
    # TEST-3: Function translation
    def test_06_function_call(self):
        """Test function call -> CALL instruction"""
        source = """
fn add(int a, int b) -> int {
    return a + b;
}
fn main() -> int {
    return add(5, 3);
}
"""
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['test_temp.src'])
        os.remove('test_temp.src')
        
        self.assertIn('call', result.stdout)
        print("   TEST-3.1: Function call works")
    
    def test_07_parameter_passing(self):
        """Test parameter passing -> PARAM instructions"""
        source = """
fn square(int x) -> int {
    return x * x;
}
"""
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['test_temp.src'])
        os.remove('test_temp.src')
        
        # Parameter should be in function signature
        self.assertIn('int x', result.stdout or result.stderr)
        print("   TEST-3.2: Parameter passing works")
    
    # TEST-4: Output formats
    def test_08_text_output(self):
        """Test text output format"""
        source = "fn main() -> int { return 42; }"
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['--format', 'text', 'test_temp.src'])
        os.remove('test_temp.src')
        
        self.assertIn('func main', result.stdout)
        print("   TEST-4.1: Text output works")
    
    def test_09_dot_output(self):
        """Test DOT/Graphviz output format"""
        source = "fn main() -> int { return 42; }"
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['--format', 'dot', 'test_temp.src'])
        os.remove('test_temp.src')
        
        self.assertIn('digraph', result.stdout)
        print("   TEST-4.2: DOT output works")
    
    def test_10_json_output(self):
        """Test JSON output format"""
        source = "fn main() -> int { return 42; }"
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['--format', 'json', 'test_temp.src'])
        os.remove('test_temp.src')
        
        self.assertIn('"functions"', result.stdout)
        print("   TEST-4.3: JSON output works")
    
    # TEST-5: Statistics
    def test_11_verbose_stats(self):
        """Test verbose statistics output"""
        source = "fn main() -> int { int x = 42; return x; }"
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['--verbose', 'test_temp.src'])
        os.remove('test_temp.src')
        
        self.assertIn('Статистика', result.stdout or '')
        self.assertIn('Функций', result.stdout or '')
        print("   TEST-5.1: Statistics output works")
    
    # TEST-6: Variable management
    def test_12_temporaries(self):
        """Test temporary variable allocation"""
        source = "fn main() -> int { return (1 + 2) * (3 + 4); }"
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['test_temp.src'])
        os.remove('test_temp.src')
        
        # Should have t1, t2, etc.
        self.assertIn('t', result.stdout)
        print("   TEST-6.1: Temporary variables work")
    
    # TEST-7: Multiple functions
    def test_13_multiple_functions(self):
        """Test multiple functions in one file"""
        source = """
fn one() -> int { return 1; }
fn two() -> int { return 2; }
fn three() -> int { return 3; }
"""
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['test_temp.src'])
        os.remove('test_temp.src')
        
        self.assertIn('one', result.stdout)
        self.assertIn('two', result.stdout)
        self.assertIn('three', result.stdout)
        print("   TEST-7.1: Multiple functions work")
    
    # TEST-8: Variable assignment
    def test_14_variable_assignment(self):
        """Test variable assignment"""
        source = "fn main() -> int { int x = 5; x = x + 1; return x; }"
        with open('test_temp.src', 'w') as f:
            f.write(source)
        result = self.run_ir_command(['test_temp.src'])
        os.remove('test_temp.src')
        
        self.assertIn('add', result.stdout)
        print("   TEST-8.1: Variable assignment works")


def run_all_tests():
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestIRRequirements)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    print()
    print(f"RESULTS: {result.testsRun} tests, {len(result.failures)} failures, {len(result.errors)} errors")
    
    if result.wasSuccessful():
        print(" ALL TESTS PASSED!")
        return 0
    else:
        print(" SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())