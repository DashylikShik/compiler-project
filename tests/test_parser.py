#!/usr/bin/env python3
import sys
import os
import glob

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.utils.ast_printer import ASTPrinter

class ParserTestRunner:
    def __init__(self):
        self.test_dir = os.path.dirname(__file__)
        self.valid_dir = os.path.join(self.test_dir, 'parser', 'valid')
        self.invalid_dir = os.path.join(self.test_dir, 'parser', 'invalid')
        self.expected_dir = os.path.join(self.test_dir, 'parser', 'expected')
        self.output_dir = os.path.join(self.test_dir, 'parser', 'output')
        os.makedirs(self.expected_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        self.passed = 0
        self.failed = 0
        self.total = 0

    def print_header(self, text):
        print(f"\n{text}")

    def normalize_ast(self, ast_text):
        lines = [line.rstrip() for line in ast_text.split('\n') if line.strip() and not line.startswith('#')]
        return '\n'.join(lines)

    def run_valid_test(self, src_file):
        self.total += 1
        rel_path = os.path.relpath(src_file, self.valid_dir)
        test_name = rel_path.replace('\\', '/')
        expected_file = os.path.join(self.expected_dir, 'valid_' + test_name.replace('.src', '.expected'))
        output_file = os.path.join(self.output_dir, 'valid_' + test_name.replace('.src', '.output'))

        os.makedirs(os.path.dirname(expected_file), exist_ok=True)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()

        scanner = Scanner(source)
        if scanner.errors:
            print(f" {test_name} - ошибки лексера")
            for err in scanner.errors:
                print(f"    {err}")
            self.failed += 1
            return False

        parser = Parser(scanner.tokens)
        ast = parser.parse()
        
        # Сохраняем AST
        ast_text = ASTPrinter.print(ast)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(ast_text)

        # Проверяем наличие expected
        if not os.path.exists(expected_file):
            print(f" {test_name} - нет expected файла, создаю...")
            with open(expected_file, 'w', encoding='utf-8') as f:
                f.write(ast_text)
            print(f" {test_name} (создан expected)")
            self.passed += 1
            return True

        # Сравниваем
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected = self.normalize_ast(f.read())
        actual = self.normalize_ast(ast_text)

        if expected == actual:
            print(f" {test_name}")
            self.passed += 1
            return True
        else:
            print(f" {test_name} - AST не совпадает")
            print(f"   Ожидалось: {expected_file}")
            print(f"   Получено: {output_file}")
            self.failed += 1
            return False

    def run_invalid_test(self, src_file):
        self.total += 1
        rel_path = os.path.relpath(src_file, self.invalid_dir)
        test_name = rel_path.replace('\\', '/')
        expected_file = os.path.join(self.expected_dir, 'invalid_' + test_name.replace('.src', '.expected'))
        output_file = os.path.join(self.output_dir, 'invalid_' + test_name.replace('.src', '.output'))

        os.makedirs(os.path.dirname(expected_file), exist_ok=True)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()

        scanner = Scanner(source)
        parser = Parser(scanner.tokens)
        parser.parse()
        
        # Сохраняем ошибки
        error_text = "\n".join(parser.errors) if parser.errors else ""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(error_text)

        # Проверяем наличие expected
        if not os.path.exists(expected_file):
            print(f" {test_name} - нет expected файла, создаю...")
            with open(expected_file, 'w', encoding='utf-8') as f:
                f.write(error_text if error_text else "EXPECTED ERRORS HERE")
            print(f" {test_name} (создан expected)")
            self.passed += 1
            return True

        # Сравниваем ошибки
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected = f.read().strip()
        actual = error_text.strip()

        if expected == actual:
            print(f" {test_name}")
            self.passed += 1
            return True
        else:
            print(f" {test_name} - ошибки не совпадают")
            print(f"   Ожидалось: {expected_file}")
            print(f"   Получено: {output_file}")
            if expected and actual:
                print(f"   Ожидаемые ошибки: {expected}")
                print(f"   Полученные ошибки: {actual}")
            self.failed += 1
            return False

    def run_all_tests(self):
        self.print_header("TEST RUNNER PARSER SPRINT 2")

        self.print_header("VALID TESTS")
        for root, _, files in os.walk(self.valid_dir):
            for file in sorted(files):
                if file.endswith('.src'):
                    self.run_valid_test(os.path.join(root, file))

        self.print_header("INVALID TESTS")
        for root, _, files in os.walk(self.invalid_dir):
            for file in sorted(files):
                if file.endswith('.src'):
                    self.run_invalid_test(os.path.join(root, file))

        self.print_header("РЕЗУЛЬТАТЫ")
        print(f"  Всего тестов: {self.total}")
        print(f"   Пройдено: {self.passed}")
        print(f"   Провалено: {self.failed}")
        if self.failed == 0:
            print("\n   ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        else:
            print(f"\n    Провалено: {self.failed} из {self.total}")

def generate_all_expected():
    """Генерирует expected файлы для ВСЕХ тестов"""
    runner = ParserTestRunner()
    runner.print_header("ГЕНЕРАЦИЯ EXPECTED ФАЙЛОВ (ВСЕ 13 ТЕСТОВ)")
    count = 0
    
    # Валидные тесты
    for root, _, files in os.walk(runner.valid_dir):
        for file in files:
            if file.endswith('.src'):
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(src_file, runner.valid_dir)
                expected_file = os.path.join(runner.expected_dir, 'valid_' + rel_path.replace('.src', '.expected'))
                os.makedirs(os.path.dirname(expected_file), exist_ok=True)
                
                with open(src_file, 'r') as f:
                    source = f.read()
                
                scanner = Scanner(source)
                if scanner.errors:
                    print(f" valid/{rel_path} - ошибки лексера")
                    continue
                
                parser = Parser(scanner.tokens)
                ast = parser.parse()
                if parser.errors:
                    print(f" valid/{rel_path} - ошибки парсера")
                    continue
                
                ast_text = ASTPrinter.print(ast)
                with open(expected_file, 'w', encoding='utf-8') as f:
                    f.write(ast_text)
                print(f" valid/{rel_path}")
                count += 1
    
    # Невалидные тесты
    for root, _, files in os.walk(runner.invalid_dir):
        for file in files:
            if file.endswith('.src'):
                src_file = os.path.join(root, file)
                rel_path = os.path.relpath(src_file, runner.invalid_dir)
                expected_file = os.path.join(runner.expected_dir, 'invalid_' + rel_path.replace('.src', '.expected'))
                os.makedirs(os.path.dirname(expected_file), exist_ok=True)
                
                with open(src_file, 'r') as f:
                    source = f.read()
                
                scanner = Scanner(source)
                parser = Parser(scanner.tokens)
                parser.parse()
                
                error_text = "\n".join(parser.errors) if parser.errors else "EXPECTED ERRORS HERE"
                with open(expected_file, 'w', encoding='utf-8') as f:
                    f.write(error_text)
                print(f" invalid/{rel_path}")
                count += 1
    
    print(f"\n Сгенерировано {count} expected файлов (13 тестов)")

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--generate":
            generate_all_expected()
        elif sys.argv[1] == "--help":
            print("Использование:")
            print("  python tests/test_parser.py           # запустить тесты")
            print("  python tests/test_parser.py --generate # создать expected (13 файлов)")
    else:
        runner = ParserTestRunner()
        runner.run_all_tests()

if __name__ == "__main__":
    main()