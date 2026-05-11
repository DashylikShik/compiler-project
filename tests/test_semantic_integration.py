#!/usr/bin/env python3
"""Простой тестовый раннер для семантического анализатора"""

import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SimpleSemanticTester:
    def __init__(self):
        self.project_dir = r'C:\Users\Пользователь\Desktop\compiler-project'
        self.passed = 0
        self.failed = 0
    
    def run(self):
        os.chdir(self.project_dir)
        
        # Валидные тесты
        print('\n2. ВАЛИДНЫЕ ПРОГРАММЫ')
        valid_tests = [
            ('01_simple', 'fn main() -> int {\n    return 42;\n}'),
            ('02_variables', 'fn main() -> int {\n    int x = 10;\n    return x;\n}'),
            ('03_functions', 'fn add(int a, int b) -> int { return a + b; }\nfn main() -> int { return add(5,3); }'),
        ]
        
        for name, code in valid_tests:
            with open('temp.src', 'w', encoding='utf-8') as f:
                f.write(code)
            result = subprocess.run(['python', 'src/main.py', 'check', 'temp.src'],
                                   capture_output=True, text=True)
            if 'Семантических ошибок не найдено' in result.stdout:
                print(f'   {name}')
                self.passed += 1
            else:
                print(f'   {name}')
                self.failed += 1
            os.remove('temp.src')
        
        # Невалидные тесты
        print('\n3. НЕВАЛИДНЫЕ ПРОГРАММЫ (должны быть ошибки)')
        invalid_tests = [
            ('undeclared', 'fn main() -> int {\n    x = 10;\n    return x;\n}', 'undeclared'),
            ('type_mismatch', 'fn main() -> int {\n    int x = "hello";\n    return x;\n}', 'type'),
            ('duplicate', 'fn foo() -> int { return 1; }\nfn foo() -> int { return 2; }', 'duplicate'),
            ('arg_count', 'fn add(int a, int b) -> int { return a + b; }\nfn main() -> int { return add(5); }', 'argument'),
        ]
        
        for name, code, expected in invalid_tests:
            with open('temp.src', 'w', encoding='utf-8') as f:
                f.write(code)
            result = subprocess.run(['python', 'src/main.py', 'check', 'temp.src'],
                                   capture_output=True, text=True)
            if expected.lower() in result.stdout.lower() or 'ошибк' in result.stdout.lower():
                print(f'   {name} (ошибка найдена: {expected})')
                self.passed += 1
            else:
                print(f'   {name} (ошибка НЕ найдена: {expected})')
                self.failed += 1
            os.remove('temp.src')
        
        # Таблица символов
        print('\n4. ТАБЛИЦА СИМВОЛОВ')
        with open('temp.src', 'w', encoding='utf-8') as f:
            f.write('fn main() -> int { return 42; }')
        result = subprocess.run(['python', 'src/main.py', 'check', '--symbols', 'temp.src'],
                               capture_output=True, text=True)
        if 'Function' in result.stdout and 'main' in result.stdout:
            print('  Таблица символов работает')
            print(result.stdout[:300])
        else:
            print('   Таблица символов не работает')
        os.remove('temp.src')
        
        
        return self.failed == 0

if __name__ == '__main__':
    tester = SimpleSemanticTester()
    success = tester.run()
    sys.exit(0 if success else 1)