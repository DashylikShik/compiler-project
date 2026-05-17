#!/usr/bin/env python3
"""Test runner for Sprint 5 - x86-64 code generation"""

import os
import sys
import subprocess
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))


class Sprint5Tester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    
    def test_simple_return(self):
        """Test: function returns constant"""
        print("\n Simple return")
        
        source = "fn main() -> int { return 42; }"
        
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
            
            if result.returncode != 0 or not os.path.exists(asm_file):
                print("   Compilation failed")
                self.failed += 1
                return
            
            with open(asm_file, 'r', encoding='utf-8') as f:
                asm = f.read()
            
            # Check required patterns
            checks = [
                ('section .text', "Text section"),
                ('global main', "Global declaration"),
                ('main:', "Function label"),
                ('push rbp', "Prologue - save RBP"),
                ('mov rbp, rsp', "Set frame pointer"),
                ('mov rax, 42', "Return value in RAX"),
                ('pop rbp', "Epilogue - restore RBP"),
                ('ret', "Return instruction"),
            ]
            
            all_ok = True
            for pattern, name in checks:
                if pattern in asm:
                    print(f"     {name}")
                else:
                    print(f"     {name}")
                    all_ok = False
            
            if all_ok:
                print("   Simple return PASSED")
                self.passed += 1
            else:
                print("   Simple return FAILED")
                self.failed += 1
                
        except Exception as e:
            print(f"   Error: {e}")
            self.failed += 1
        finally:
            for f in [src_file, asm_file]:
                if f and os.path.exists(f):
                    os.remove(f)
    
    def test_arithmetic(self):
        """Test: arithmetic operations"""
        print("\n Arithmetic operations")        
        source = "fn main() -> int { return 2 + 3 * 4; }"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.src', delete=False, encoding='utf-8') as f:
            f.write(source)
            src_file = f.name
        
        asm_file = src_file.replace('.src', '.asm')
        
        try:
            result = subprocess.run(
                ['python', 'src/main.py', 'compile', src_file, '--output', asm_file],
                capture_output=True, text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0 or not os.path.exists(asm_file):
                print("   Compilation failed")
                self.failed += 1
                return
            
            with open(asm_file, 'r', encoding='utf-8') as f:
                asm = f.read()
            
            checks = [
                ('imul', "Multiplication (IMUL)"),
                ('add', "Addition (ADD)"),
                ('mov eax', "Move to EAX"),
            ]
            
            all_ok = True
            for pattern, name in checks:
                if pattern in asm:
                    print(f"     {name}")
                else:
                    print(f"     {name}")
                    all_ok = False
            
            if all_ok:
                print("   Arithmetic operations PASSED")
                self.passed += 1
            else:
                print("   Arithmetic operations FAILED")
                self.failed += 1
                
        except Exception as e:
            print(f"   Error: {e}")
            self.failed += 1
        finally:
            for f in [src_file, asm_file]:
                if f and os.path.exists(f):
                    os.remove(f)
    
    def test_variables(self):
        """Test: variables on stack"""
        print("\n Variables on stack")
        
        source = "fn main() -> int { int x = 10; int y = 20; return x + y; }"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.src', delete=False, encoding='utf-8') as f:
            f.write(source)
            src_file = f.name
        
        asm_file = src_file.replace('.src', '.asm')
        
        try:
            result = subprocess.run(
                ['python', 'src/main.py', 'compile', src_file, '--output', asm_file],
                capture_output=True, text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0 or not os.path.exists(asm_file):
                print("   Compilation failed")
                self.failed += 1
                return
            
            with open(asm_file, 'r', encoding='utf-8') as f:
                asm = f.read()
            
            checks = [
                ('sub rsp', "Stack allocation"),
                ('mov [rbp-', "Store to stack"),
                ('mov eax, [rbp-', "Load from stack"),
                ('add eax, [rbp-', "Add from stack"),
            ]
            
            all_ok = True
            for pattern, name in checks:
                if pattern in asm:
                    print(f"     {name}")
                else:
                    print(f"     {name}")
                    all_ok = False
            
            if all_ok:
                print("   Variables on stack PASSED")
                self.passed += 1
            else:
                print("   Variables on stack FAILED")
                self.failed += 1
                
        except Exception as e:
            print(f"   Error: {e}")
            self.failed += 1
        finally:
            for f in [src_file, asm_file]:
                if f and os.path.exists(f):
                    os.remove(f)
    
    def test_if_statement(self):
        """Test: if statement with jumps"""
        print("\n If statement")
        
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.src', delete=False, encoding='utf-8') as f:
            f.write(source)
            src_file = f.name
        
        asm_file = src_file.replace('.src', '.asm')
        
        try:
            result = subprocess.run(
                ['python', 'src/main.py', 'compile', src_file, '--output', asm_file],
                capture_output=True, text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0 or not os.path.exists(asm_file):
                print("   Compilation failed")
                self.failed += 1
                return
            
            with open(asm_file, 'r', encoding='utf-8') as f:
                asm = f.read()
            
            checks = [
                ('cmp', "Compare instruction"),
                ('jne', "Conditional jump (JNE)"),
                ('jmp', "Unconditional jump (JMP)"),
            ]
            
            all_ok = True
            for pattern, name in checks:
                if pattern in asm:
                    print(f"     {name}")
                else:
                    print(f"     {name}")
                    all_ok = False
            
            if all_ok:
                print("   If statement PASSED")
                self.passed += 1
            else:
                print("   If statement FAILED")
                self.failed += 1
                
        except Exception as e:
            print(f"   Error: {e}")
            self.failed += 1
        finally:
            for f in [src_file, asm_file]:
                if f and os.path.exists(f):
                    os.remove(f)
    
    def test_while_loop(self):
        """Test: while loop"""
        print("\n While loop")
        
        source = """
fn main() -> int {
    int i = 0;
    while (i < 5) {
        i = i + 1;
    }
    return i;
}
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.src', delete=False, encoding='utf-8') as f:
            f.write(source)
            src_file = f.name
        
        asm_file = src_file.replace('.src', '.asm')
        
        try:
            result = subprocess.run(
                ['python', 'src/main.py', 'compile', src_file, '--output', asm_file],
                capture_output=True, text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0 or not os.path.exists(asm_file):
                print("   Compilation failed")
                self.failed += 1
                return
            
            with open(asm_file, 'r', encoding='utf-8') as f:
                asm = f.read()
            
            has_cmp = 'cmp' in asm
            has_jump = 'jmp' in asm or 'je' in asm or 'jne' in asm
            
            if has_cmp:
                print("     Compare instruction found")
            else:
                print("     Compare instruction missing")
            
            if has_jump:
                print("     Jump instruction found")
            else:
                print("     Jump instruction missing")
            
            if has_cmp and has_jump:
                print("   While loop PASSED")
                self.passed += 1
            else:
                print("   While loop FAILED")
                self.failed += 1
                
        except Exception as e:
            print(f"   Error: {e}")
            self.failed += 1
        finally:
            for f in [src_file, asm_file]:
                if f and os.path.exists(f):
                    os.remove(f)
    
    def test_function_call(self):
        """Test: function call with parameters"""
        print("\n Function call")
        
        source = """
fn add(int a, int b) -> int {
    return a + b;
}
fn main() -> int {
    return add(5, 3);
}
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.src', delete=False, encoding='utf-8') as f:
            f.write(source)
            src_file = f.name
        
        asm_file = src_file.replace('.src', '.asm')
        
        try:
            result = subprocess.run(
                ['python', 'src/main.py', 'compile', src_file, '--output', asm_file],
                capture_output=True, text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0 or not os.path.exists(asm_file):
                print("   Compilation failed")
                self.failed += 1
                return
            
            with open(asm_file, 'r', encoding='utf-8') as f:
                asm = f.read()
            
            checks = [
                ('add:', "Function add label"),
                ('main:', "Function main label"),
                ('call add', "Call instruction"),
                ('mov edi', "First parameter (RDI)"),
                ('mov esi', "Second parameter (RSI)"),
            ]
            
            all_ok = True
            for pattern, name in checks:
                if pattern in asm:
                    print(f"     {name}")
                else:
                    print(f"     {name}")
                    all_ok = False
            
            if all_ok:
                print("   Function call PASSED")
                self.passed += 1
            else:
                print("   Function call FAILED")
                self.failed += 1
                
        except Exception as e:
            print(f"   Error: {e}")
            self.failed += 1
        finally:
            for f in [src_file, asm_file]:
                if f and os.path.exists(f):
                    os.remove(f)
    
    def test_abi_compliance(self):
        """Test: ABI compliance"""
        print("\n ABI compliance")
        
        source = "fn main() -> int { return 42; }"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.src', delete=False, encoding='utf-8') as f:
            f.write(source)
            src_file = f.name
        
        asm_file = src_file.replace('.src', '.asm')
        
        try:
            result = subprocess.run(
                ['python', 'src/main.py', 'compile', src_file, '--output', asm_file],
                capture_output=True, text=True,
                cwd=self.project_root
            )
            
            if result.returncode != 0 or not os.path.exists(asm_file):
                print("   Compilation failed")
                self.failed += 1
                return
            
            with open(asm_file, 'r', encoding='utf-8') as f:
                asm = f.read()
            
            checks = [
                ('mov rax, 42', "Return value in RAX"),
                ('ret', "Return instruction"),
            ]
            
            all_ok = True
            for pattern, name in checks:
                if pattern in asm:
                    print(f"     {name}")
                else:
                    print(f"     {name}")
                    all_ok = False
            
            if all_ok:
                print("   ABI compliance PASSED")
                self.passed += 1
            else:
                print("   ABI compliance FAILED")
                self.failed += 1
                
        except Exception as e:
            print(f"   Error: {e}")
            self.failed += 1
        finally:
            for f in [src_file, asm_file]:
                if f and os.path.exists(f):
                    os.remove(f)
    
    def run(self):
        """Run all tests"""
        
        # Run all tests
        self.test_simple_return()
        self.test_arithmetic()
        self.test_variables()
        self.test_if_statement()
        self.test_while_loop()
        self.test_function_call()
        self.test_abi_compliance()
        


if __name__ == "__main__":
    tester = Sprint5Tester()
    success = tester.run()
    sys.exit(0 if success else 1)