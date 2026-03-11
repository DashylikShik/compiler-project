#!/usr/bin/env python3
"""
Test Runner для Lexer
20 валидных + 10 невалидных = 30 тестов с expected файлами
"""

import sys
import os
import glob

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.lexer.scanner import Scanner

class TestRunner:
    def __init__(self):
        self.test_dir = os.path.dirname(__file__)
        
        # Пути к папкам
        self.valid_dir = os.path.join(self.test_dir, 'lexer', 'valid')
        self.invalid_dir = os.path.join(self.test_dir, 'lexer', 'invalid')
        self.expected_dir = os.path.join(self.test_dir, 'lexer', 'expected')
        self.output_dir = os.path.join(self.test_dir, 'lexer', 'output')
        
        # Создаем папки
        os.makedirs(self.expected_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Счетчики
        self.passed = 0
        self.failed = 0
    
    def print_header(self, text):
        print(f"\n{text}")
    
    
    def run_valid_test(self, src_file):
        """Запускает валидный тест - сравнивает токены с expected"""
        test_name = os.path.basename(src_file).replace('.src', '')
        expected_file = os.path.join(self.expected_dir, f"{test_name}.expected")
        output_file = os.path.join(self.output_dir, f"{test_name}.output")
        
        # Проверяем наличие ожидаемого файла
        if not os.path.exists(expected_file):
            print(f"   {test_name} - нет файла .expected (запусти --generate)")
            self.failed += 1
            return False
        
        # Читаем исходный код
        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Запускаем сканер
        scanner = Scanner(source)
        
        # Для валидных тестов НЕ ДОЛЖНО быть ошибок
        if scanner.errors:
            print(f"   {test_name} - найдены ошибки в валидном коде!")
            for err in scanner.errors[:3]:
                print(f"       {err}")
            self.failed += 1
            return False
        
        # Сохраняем вывод токенов
        output_lines = []
        for token in scanner.tokens:
            if token.literal_value is not None:
                output_lines.append(f"{token.line}:{token.column} {token.type.value} \"{token.lexeme}\" {token.literal_value}")
            else:
                output_lines.append(f"{token.line}:{token.column} {token.type.value} \"{token.lexeme}\"")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        # Читаем ожидаемый файл (без комментариев)
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected_lines = [line for line in f.read().split('\n') 
                            if line.strip() and not line.startswith('#')]
        
        # Сравниваем
        if expected_lines == output_lines:
            print(f"   {test_name}")
            self.passed += 1
            return True
        else:
            print(f"   {test_name}")
            print(f"      Ожидалось: {len(expected_lines)} строк, Получено: {len(output_lines)} строк")
            self.failed += 1
            return False
    
    
    def run_invalid_test(self, src_file):
        """Запускает невалидный тест - сравнивает ошибки с expected"""
        test_name = os.path.basename(src_file).replace('.src', '')
        expected_file = os.path.join(self.expected_dir, f"{test_name}.expected")
        output_file = os.path.join(self.output_dir, f"{test_name}.output")
        
        # Проверяем наличие ожидаемого файла
        if not os.path.exists(expected_file):
            print(f"   {test_name} - нет файла .expected (запусти --generate)")
            self.failed += 1
            return False
        
        # Читаем исходный код
        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Запускаем сканер
        scanner = Scanner(source)
        
        # Сохраняем ошибки
        output_lines = []
        for error in scanner.errors:
            output_lines.append(error)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        # Читаем ожидаемые ошибки
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected_lines = [line for line in f.read().split('\n') 
                            if line.strip() and not line.startswith('#')]
        
        # Сравниваем
        if expected_lines == output_lines:
            print(f"   {test_name} (найдено ошибок: {len(output_lines)})")
            self.passed += 1
            return True
        else:
            print(f"   {test_name}")
            print(f"      Ожидалось ошибок: {len(expected_lines)}, Получено: {len(output_lines)}")
            self.failed += 1
            return False
    
    #  ГЕНЕРАЦИЯ EXPECTED ДЛЯ ВАЛИДНЫХ ТЕСТОВ
    def generate_expected_valid(self, src_file):
        """Генерирует .expected для валидного теста (токены)"""
        test_name = os.path.basename(src_file).replace('.src', '')
        expected_file = os.path.join(self.expected_dir, f"{test_name}.expected")
        
        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        scanner = Scanner(source)
        
        # Если есть ошибки - не генерируем
        if scanner.errors:
            print(f"   {test_name} - В КОДЕ ЕСТЬ ОШИБКИ! Файл НЕ создан")
            for err in scanner.errors:
                print(f"       {err}")
            return False
        
        # Генерируем токены
        lines = [f"# Test: {test_name}", f"# Type: valid", "#" + "-" * 50]
        
        for token in scanner.tokens:
            if token.literal_value is not None:
                lines.append(f"{token.line}:{token.column} {token.type.value} \"{token.lexeme}\" {token.literal_value}")
            else:
                lines.append(f"{token.line}:{token.column} {token.type.value} \"{token.lexeme}\"")
        
        with open(expected_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"   {test_name}.expected (valid)")
        return True
    
    # ГЕНЕРАЦИЯ EXPECTED ДЛЯ НЕВАЛИДНЫХ ТЕСТОВ
    
    def generate_expected_invalid(self, src_file):
        """Генерирует .expected для невалидного теста (список ошибок)"""
        test_name = os.path.basename(src_file).replace('.src', '')
        expected_file = os.path.join(self.expected_dir, f"{test_name}.expected")
        
        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        scanner = Scanner(source)
        
        # Генерируем список ошибок
        lines = [
            f"# Test: {test_name}",
            f"# Type: invalid",
            f"# Expected errors: {len(scanner.errors)}",
        ]
        
        for error in scanner.errors:
            lines.append(error)
        
        with open(expected_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"   {test_name}.expected (invalid, {len(scanner.errors)} ошибок)")
        return True
    
    #ГЕНЕРАЦИЯ ВСЕХ EXPECTED
    
    def generate_all_expected(self):
        """Генерирует все expected файлы (20 valid + 10 invalid)"""
        self.print_header("ГЕНЕРАЦИЯ EXPECTED ФАЙЛОВ (30 шт)")
        
        valid_count = 0
        invalid_count = 0
        
        # Валидные тесты
        print("\nVALID TESTS:")
        valid_files = sorted(glob.glob(os.path.join(self.valid_dir, '*.src')))
        for src_file in valid_files:
            if self.generate_expected_valid(src_file):
                valid_count += 1
        
        # Невалидные тесты
        print("\nINVALID TESTS:")
        invalid_files = sorted(glob.glob(os.path.join(self.invalid_dir, '*.src')))
        for src_file in invalid_files:
            if self.generate_expected_invalid(src_file):
                invalid_count += 1
        
        total = valid_count + invalid_count
        print(f"\n Сгенерировано: {valid_count} valid + {invalid_count} invalid = {total} expected файлов")
    
    
    def run_all_tests(self):
        """Запускает все 30 тестов"""
        
        self.passed = 0
        self.failed = 0
        
        # Валидные тесты
        self.print_header("VALID TESTS (20 шт) - сравнение токенов")
        valid_files = sorted(glob.glob(os.path.join(self.valid_dir, '*.src')))
        for test_file in valid_files:
            self.run_valid_test(test_file)
        
        # Невалидные тесты
        self.print_header("INVALID TESTS (10 шт) - сравнение ошибок")
        invalid_files = sorted(glob.glob(os.path.join(self.invalid_dir, '*.src')))
        for test_file in invalid_files:
            self.run_invalid_test(test_file)
        
        # Результаты
        self.print_header("РЕЗУЛЬТАТЫ")
        print(f"  Всего тестов: 30 (20 valid + 10 invalid)")
        print(f"   Пройдено: {self.passed}")
        print(f"   Провалено: {self.failed}")
        
        if self.failed == 0:
            print("\n   ВСЕ 30 ТЕСТОВ ПРОЙДЕНЫ!")
        else:
            print(f"\n    Провалено: {self.failed} из 30")

# СОЗДАНИЕ ТЕСТОВЫХ ФАЙЛОВ

def create_test_files():
    """Создает 20 валидных и 10 невалидных тестов"""
    
    valid_dir = os.path.join(os.path.dirname(__file__), 'lexer', 'valid')
    invalid_dir = os.path.join(os.path.dirname(__file__), 'lexer', 'invalid')
    
    os.makedirs(valid_dir, exist_ok=True)
    os.makedirs(invalid_dir, exist_ok=True)

    # 20 ВАЛИДНЫХ ТЕСТОВ (код из твоего файла)
    valid_tests = {
        '01_identifiers.src': "// Идентификаторы\ncounter\ntemp\nresult\n_private\nvalue123",
        '02_numbers.src': "// Целые числа\n0\n42\n1000\n-5\n2147483647\n-2147483648",
        '03_floats.src': "// Числа с точкой\n3.14\n0.5\n10.0\n-0.001\n999.999",
        # ... (остальные тесты как у тебя)
    }
    
    # 10 НЕВАЛИДНЫХ ТЕСТОВ
    invalid_tests = {
        '01_invalid_char.src': "// Недопустимые символы\n@invalid\n#invalid\n$invalid\n`invalid",
        '02_unterminated_string.src': "// Незакрытая строка\n\"unterminated string\nint x = 42;",
        # ... (остальные тесты как у тебя)
    }
    
    # Создаем файлы
    print("Создание 20 ВАЛИДНЫХ тестов...")
    for filename, content in valid_tests.items():
        path = os.path.join(valid_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"  + {filename}")
    
    print("\nСоздание 10 НЕВАЛИДНЫХ тестов...")
    for filename, content in invalid_tests.items():
        path = os.path.join(invalid_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"  + {filename}")
    
    print(f"\n СОЗДАНО: 20 valid + 10 invalid = 30 тестов")


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--create":
            create_test_files()
        elif sys.argv[1] == "--generate":
            runner = TestRunner()
            runner.generate_all_expected()
        elif sys.argv[1] == "--help":
            print("\nИспользование:")
            print("  python tests/test_runner.py           # запустить тесты")
            print("  python tests/test_runner.py --create  # создать файлы тестов")
            print("  python tests/test_runner.py --generate # создать .expected файлы")
            print("  python tests/test_runner.py --help    # показать помощь")
        else:
            print(f"Неизвестная команда: {sys.argv[1]}")
    else:
        runner = TestRunner()
        runner.run_all_tests()

if __name__ == "__main__":
    main()