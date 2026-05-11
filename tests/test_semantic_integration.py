#!/usr/bin/env python3
"""
Test Runner для Semantic Analyzer
Валидные и невалидные тесты с expected файлами
"""

import sys
import os
import glob

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer


class SemanticTestRunner:
    def __init__(self):
        self.test_dir = os.path.dirname(__file__)
        
        # Пути к папкам для семантических тестов
        self.valid_dir = os.path.join(self.test_dir, 'semantic', 'valid')
        self.invalid_dir = os.path.join(self.test_dir, 'semantic', 'invalid')
        self.expected_dir = os.path.join(self.test_dir, 'semantic', 'expected')
        self.output_dir = os.path.join(self.test_dir, 'semantic', 'output')
        
        # Создаем папки
        os.makedirs(self.expected_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Счетчики
        self.passed = 0
        self.failed = 0
    
    def print_header(self, text):
        print(f"\n{text}")
        print("=" * 60)
    
    def run_valid_test(self, src_file):
        """Запускает валидный тест - сравнивает результат с expected"""
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
        
        # Лексический анализ
        scanner = Scanner(source)
        if scanner.errors:
            print(f"   {test_name} - ЛЕКСИЧЕСКИЕ ОШИБКИ в валидном тесте!")
            for err in scanner.errors[:3]:
                print(f"       {err}")
            self.failed += 1
            return False
        
        # Синтаксический анализ
        parser = Parser(scanner.tokens)
        try:
            ast = parser.parse()
        except Exception as e:
            print(f"   {test_name} - СИНТАКСИЧЕСКАЯ ОШИБКА: {e}")
            self.failed += 1
            return False
        
        if parser.errors:
            print(f"   {test_name} - СИНТАКСИЧЕСКИЕ ОШИБКИ в валидном тесте!")
            for err in parser.errors[:3]:
                print(f"       {err}")
            self.failed += 1
            return False
        
        # Семантический анализ
        analyzer = SemanticAnalyzer(verbose=False)
        analyzer.analyze(ast, source)
        
        # Для валидных тестов НЕ ДОЛЖНО быть ошибок
        if analyzer.has_errors():
            print(f"   {test_name} - СЕМАНТИЧЕСКИЕ ОШИБКИ в валидном коде!")
            for err in analyzer.get_errors()[:3]:
                print(f"       {err}")
            self.failed += 1
            return False
        
        # Сохраняем вывод (таблица символов)
        output_lines = []
        output_lines.append("SEMANTIC ANALYSIS SUCCESSFUL")
        output_lines.append("")
        output_lines.append(analyzer.get_symbol_table().dump())
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        # Читаем ожидаемый файл
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected_lines = [line.rstrip() for line in f.read().split('\n') 
                            if line and not line.startswith('#')]
        
        # Сравниваем
        output_lines_clean = [line for line in output_lines if line.strip()]
        
        if expected_lines == output_lines_clean:
            print(f"   ✅ {test_name}")
            self.passed += 1
            return True
        else:
            print(f"   ❌ {test_name}")
            print(f"      Ожидалось: {len(expected_lines)} строк, Получено: {len(output_lines_clean)} строк")
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
        
        # Лексический анализ
        scanner = Scanner(source)
        parser = Parser(scanner.tokens)
        
        try:
            ast = parser.parse()
        except Exception as e:
            # Синтаксическая ошибка - это тоже ошибка
            output_lines = [f"SYNTAX ERROR: {e}"]
        else:
            if parser.errors:
                output_lines = parser.errors
            else:
                # Семантический анализ
                analyzer = SemanticAnalyzer(verbose=False)
                analyzer.analyze(ast, source)
                
                # Сохраняем ошибки
                output_lines = [str(err) for err in analyzer.get_errors()]
        
        # Сохраняем вывод
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        # Читаем ожидаемые ошибки
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected_lines = [line for line in f.read().split('\n') 
                            if line.strip() and not line.startswith('#')]
        
        # Сравниваем
        if expected_lines == output_lines:
            print(f"   ✅ {test_name} (найдено ошибок: {len(output_lines)})")
            self.passed += 1
            return True
        else:
            print(f"   ❌ {test_name}")
            print(f"      Ожидалось: {len(expected_lines)} строк, Получено: {len(output_lines)} строк")
            self.failed += 1
            return False
    
    def generate_expected_valid(self, src_file):
        """Генерирует .expected для валидного теста"""
        test_name = os.path.basename(src_file).replace('.src', '')
        expected_file = os.path.join(self.expected_dir, f"{test_name}.expected")
        
        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Полный анализ
        scanner = Scanner(source)
        parser = Parser(scanner.tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast, source)
        
        if analyzer.has_errors():
            print(f"   {test_name} - В КОДЕ ЕСТЬ ОШИБКИ! Файл НЕ создан")
            return False
        
        # Генерируем эталон
        lines = [f"# Test: {test_name}", f"# Type: valid", "#" + "-" * 50]
        lines.append("SEMANTIC ANALYSIS SUCCESSFUL")
        lines.append("")
        lines.append(analyzer.get_symbol_table().dump())
        
        with open(expected_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"   ✅ {test_name}.expected (valid)")
        return True
    
    def generate_expected_invalid(self, src_file):
        """Генерирует .expected для невалидного теста"""
        test_name = os.path.basename(src_file).replace('.src', '')
        expected_file = os.path.join(self.expected_dir, f"{test_name}.expected")
        
        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Полный анализ
        scanner = Scanner(source)
        parser = Parser(scanner.tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast, source)
        
        # Генерируем список ошибок
        lines = [
            f"# Test: {test_name}",
            f"# Type: invalid",
            f"# Expected errors: {len(analyzer.get_errors())}",
            "#" + "-" * 50
        ]
        
        for error in analyzer.get_errors():
            lines.append(str(error))
        
        with open(expected_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"   ✅ {test_name}.expected (invalid, {len(analyzer.get_errors())} ошибок)")
        return True
    
    def generate_all_expected(self):
        """Генерирует все expected файлы"""
        self.print_header("ГЕНЕРАЦИЯ EXPECTED ФАЙЛОВ")
        
        valid_count = 0
        invalid_count = 0
        
        # Валидные тесты
        print("\n📁 VALID TESTS:")
        valid_files = sorted(glob.glob(os.path.join(self.valid_dir, '*.src')))
        for src_file in valid_files:
            if self.generate_expected_valid(src_file):
                valid_count += 1
        
        # Невалидные тесты
        print("\n📁 INVALID TESTS:")
        invalid_files = sorted(glob.glob(os.path.join(self.invalid_dir, '*.src')))
        for src_file in invalid_files:
            if self.generate_expected_invalid(src_file):
                invalid_count += 1
        
        total = valid_count + invalid_count
        print(f"\n✅ Сгенерировано: {valid_count} valid + {invalid_count} invalid = {total} expected файлов")
    
    def run_all_tests(self):
        """Запускает все тесты"""
        self.passed = 0
        self.failed = 0
        
        # Валидные тесты
        self.print_header("VALID TESTS - проверка корректных программ")
        valid_files = sorted(glob.glob(os.path.join(self.valid_dir, '*.src')))
        
        if not valid_files:
            print("   ⚠️  Нет валидных тестов! Создайте .src файлы в tests/semantic/valid/")
            print("   или запустите --create для создания примеров")
        
        for test_file in valid_files:
            self.run_valid_test(test_file)
        
        # Невалидные тесты
        self.print_header("INVALID TESTS - проверка обнаружения ошибок")
        invalid_files = sorted(glob.glob(os.path.join(self.invalid_dir, '*.src')))
        
        if not invalid_files:
            print("   ⚠️  Нет невалидных тестов! Создайте .src файлы в tests/semantic/invalid/")
        
        for test_file in invalid_files:
            self.run_invalid_test(test_file)
        
        # Результаты
        self.print_header("РЕЗУЛЬТАТЫ")
        print(f"  ✅ Пройдено: {self.passed}")
        print(f"  ❌ Провалено: {self.failed}")
        print(f"  📊 Всего: {self.passed + self.failed}")
        
        if self.failed == 0 and (valid_files or invalid_files):
            print("\n  🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        elif not valid_files and not invalid_files:
            print("\n  ⚠️  Нет тестов для запуска! Используйте --create")
        else:
            print(f"\n  ⚠️  Провалено: {self.failed} тестов")
    
    def create_test_files(self):
        """Создает тестовые файлы для семантики"""
        
        # Валидные тесты
        valid_tests = {
            '01_simple.src': '''fn main() -> int {
    return 42;
}''',
            '02_variables.src': '''fn main() -> int {
    int x = 10;
    int y = 20;
    int z = x + y;
    return z;
}''',
            '03_functions.src': '''fn add(int a, int b) -> int {
    return a + b;
}

fn main() -> int {
    return add(5, 3);
}''',
            '04_nested_scope.src': '''fn main() -> int {
    int x = 10;
    if (x > 5) {
        int y = 20;
        x = x + y;
    }
    return x;
}''',
            '05_arithmetic.src': '''fn main() -> int {
    int a = 5 + 3 * 2;
    int b = (10 - 4) / 2;
    return a + b;
}'''
        }
        
        # Невалидные тесты
        invalid_tests = {
            '01_undeclared_variable.src': '''fn main() -> int {
    x = 10;
    return x;
}''',
            '02_type_mismatch.src': '''fn main() -> int {
    int x = "hello";
    return x;
}''',
            '03_duplicate_function.src': '''fn foo() -> int {
    return 1;
}

fn foo() -> int {
    return 2;
}''',
            '04_argument_count.src': '''fn add(int a, int b) -> int {
    return a + b;
}

fn main() -> int {
    return add(5);
}''',
            '05_invalid_condition.src': '''fn main() -> int {
    int x = 5;
    if (x) {
        return 1;
    }
    return 0;
}''',
            '06_return_type_mismatch.src': '''fn main() -> int {
    return true;
}'''
        }
        
        # Создаем файлы
        print("\n📝 Создание валидных тестов...")
        for filename, content in valid_tests.items():
            path = os.path.join(self.valid_dir, filename)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"  + {filename}")
        
        print("\n📝 Создание невалидных тестов...")
        for filename, content in invalid_tests.items():
            path = os.path.join(self.invalid_dir, filename)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content.strip())
            print(f"  + {filename}")
        
        print(f"\n✅ СОЗДАНО: {len(valid_tests)} valid + {len(invalid_tests)} invalid тестов")
        print("\nТеперь запустите --generate для создания expected файлов")


def main():
    runner = SemanticTestRunner()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--create":
            runner.create_test_files()
        elif sys.argv[1] == "--generate":
            runner.generate_all_expected()
        elif sys.argv[1] == "--help":
            print("\nИспользование:")
            print("  python tests/test_semantic_integration.py           # запустить тесты")
            print("  python tests/test_semantic_integration.py --create  # создать файлы тестов")
            print("  python tests/test_semantic_integration.py --generate # создать .expected файлы")
            print("  python tests/test_semantic_integration.py --help    # показать помощь")
        else:
            print(f"Неизвестная команда: {sys.argv[1]}")
    else:
        runner.run_all_tests()


if __name__ == "__main__":
    main()