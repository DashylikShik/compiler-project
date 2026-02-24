#!/usr/bin/env python3
"""
Test Runner для Lexer
Запускает все тесты из папок valid и invalid
"""

import sys
import os
import glob

# Добавляем путь к src
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.lexer.scanner import Scanner

class TestRunner:
    def __init__(self):
        self.test_dir = os.path.dirname(__file__)
        self.passed = 0
        self.failed = 0
        self.total = 0
        
    def print_header(self, text):
        """Заголовок"""
        print(f"\n{text}")
        print("-" * 50)
    
    def print_result(self, test_name, passed, actual_errors=None):
        """Печать результата теста"""
        if passed:
            print(f"  + {test_name}")
        else:
            print(f"  - {test_name}")
            if actual_errors:
                for err in actual_errors[:3]:
                    print(f"    * {err}")
    
    def run_valid_test(self, test_file):
        """Запуск valid теста (не должно быть ошибок)"""
        with open(test_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        scanner = Scanner(source)
        has_errors = len(scanner.errors) > 0
        
        test_name = os.path.basename(test_file)
        
        if not has_errors:
            self.passed += 1
            self.print_result(test_name, True)
        else:
            self.failed += 1
            self.print_result(test_name, False, scanner.errors)
        
        return not has_errors
    
    def run_invalid_test(self, test_file):
        """Запуск invalid теста (ДОЛЖНЫ быть ошибки)"""
        with open(test_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        scanner = Scanner(source)
        has_errors = len(scanner.errors) > 0
        
        test_name = os.path.basename(test_file)
        
        if has_errors:
            self.passed += 1
            self.print_result(test_name, True)
        else:
            self.failed += 1
            self.print_result(test_name, False)
        
        return has_errors
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        self.print_header("TEST RUNNER v1.0 - Лексический анализатор")
        
        # Папки с тестами
        valid_dir = os.path.join(self.test_dir, 'lexer', 'valid')
        invalid_dir = os.path.join(self.test_dir, 'lexer', 'invalid')
        
        # VALID TESTS
        self.print_header("VALID TESTS (должны работать без ошибок)")
        valid_files = sorted(glob.glob(os.path.join(valid_dir, '*.src')))
        
        for test_file in valid_files:
            self.run_valid_test(test_file)
        
        # INVALID TESTS
        self.print_header("INVALID TESTS (должны выдавать ошибки)")
        invalid_files = sorted(glob.glob(os.path.join(invalid_dir, '*.src')))
        
        for test_file in invalid_files:
            self.run_invalid_test(test_file)
        
        # RESULTS
        self.print_header("РЕЗУЛЬТАТЫ")
        print(f"  Всего тестов: {self.passed + self.failed}")
        print(f"  Пройдено: {self.passed}")
        print(f"  Провалено: {self.failed}")
        
        if self.failed == 0:
            print("\n  ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
            return True
        else:
            print(f"\n  Провалено тестов: {self.failed}")
            return False

def create_test_files():
    """Создает все необходимые тестовые файлы"""
    
    # VALID TESTS (18 штук)
    valid_tests = {
        'test_identifiers.src': """
// Тест 1: Идентификаторы
x
counter
_private
longIdentifier_with_mixedCase_123
abc123
""",
        
        'test_keywords.src': """
// Тест 2: Все ключевые слова
if else while for
int float bool return
true false void struct fn
""",
        
        'test_operators.src': """
// Тест 3: Операторы
+ - * / %
== != < <= > >=
&& || !
= += -= *= /=
""",
        
        'test_delimiters.src': """
// Тест 4: Разделители
( ) { } [ ] ; , :
fn test() { int x; }
""",
        
        'test_comments.src': """
// Тест 5: Комментарии
int x = 42; // это комментарий
/* многострочный
   комментарий */
/* вложенный /* комментарий */ test */
""",
        
        'test_strings.src': """
// Тест 6: Строки
"hello"
"hello world"
""
"line1\\nline2"
"special !@#$%"
""",
        
        'test_expressions.src': """
// Тест 7: Выражения
x + y * 2
a + b - c
(x > 10) && (y < 20)
counter += 1
""",
        
        'test_functions.src': """
// Тест 8: Функции
fn main() {
    return 0;
}
fn add(a int, b int) int {
    return a + b;
}
""",
        
        'test_conditionals.src': """
// Тест 9: Условные операторы
if (x > 0) {
    return x;
} else {
    return -x;
}
""",
        
        'test_loops.src': """
// Тест 10: Циклы
while (i < 10) {
    i = i + 1;
}
for (i = 0; i < 10; i = i + 1) {
    print(i);
}
""",
        
        'test_variables.src': """
// Тест 11: Переменные
int counter;
float price = 99.99;
bool flag = true;
counter = 42;
""",
        
        'test_types.src': """
// Тест 12: Типы данных
int i = 42;
float f = 3.14;
bool b = true;
void test() {}
""",
        
        'test_booleans.src': """
// Тест 13: Булевы значения
true
false
if (true) {}
while (false) {}
return true;
""",
        
        'test_mixed.src': """
// Тест 14: Смешанный код
fn calculate(x int, y int) int {
    int result = x * y + 42;
    if (result > 100) {
        return 100;
    }
    return result;
}
""",
        
        'test_whitespace.src': """
// Тест 15: Пробельные символы
int    x    =    42    ;
int y=42;
int z
=
99
;
""",
        
        'test_nested_comments.src': """
// Тест 16: Вложенные комментарии
/* внешний
   /* внутренний */
   еще текст */
int x = 42;
/* /* вложенный */ комментарий */
""",
        
        'test_long_identifiers.src': """
// Тест 17: Длинные идентификаторы
int this_is_a_very_long_identifier_name_that_is_still_valid_123 = 42;
float another_really_long_identifier_with_many_characters_456 = 3.14;
""",
        
        'test_all_features.src': """
// Тест 18: Все возможности
fn process(data int) int {
    int result = 0;
    float temp = 0.0;
    
    if (data > 0) {
        for (int i = 0; i < data; i = i + 1) {
            result = result + i;
        }
    } else {
        result = -1;
    }
    
    return result;
}
"""
    }
    
    # INVALID TESTS (12 штук)
    invalid_tests = {
        'test_invalid_char.src': """
// Тест 1: Недопустимые символы
int x = 42;
@invalid
#invalid
$invalid
`invalid
""",
        
        'test_unterminated_string.src': """
// Тест 2: Незакрытая строка
"unterminated string
int x = 42;
"another unterminated
""",
        
        'test_unterminated_comment.src': """
// Тест 3: Незакрытый комментарий
int x = 42;
/* этот комментарий
   никогда не закрывается
int y = 99;
""",
        
        'test_malformed_number.src': """
// Тест 4: Неправильные числа
123.456.789
.123
123.
12.34.56
""",
        
        'test_invalid_identifier.src': """
// Тест 5: Неправильные идентификаторы
int 123abc = 42;
int a@b = 99;
int a#b = 77;
""",
        
        'test_missing_quote.src': """
// Тест 6: Отсутствующая кавычка
string s = "hello;
string t = world";
string u = "test;
""",
        
        'test_invalid_operator.src': """
// Тест 7: Неправильные операторы
x & y
x | y
x ^ y
x ~ y
""",
        
        'test_empty_comment.src': """
// Тест 8: Пустые комментарии
/**/
/* */
///
/*/*/
""",
        
        'test_mixed_errors.src': """
// Тест 9: Смешанные ошибки
int @x = "unterminated;
float 123.456.789;
/* незакрытый комментарий
int y = 42;
string s = "hello;
""",
        
        'test_out_of_range.src': """
// Тест 10: Числа вне диапазона
int too_big = 2147483648;
int too_small = -2147483649;
int also_big = 9999999999;
""",
        
        'test_boundaries.src': """
// Тест 11: Граничные значения (с ошибками)
int max_int = 2147483648;   // больше 2³¹-1
int min_int = -2147483649;  // меньше -2³¹
float small = 0.0000001;
float large = 999999.999999;
""",
        
        'test_numbers.src': """
// Тест 12: Числа с проверкой границ
42
2147483647
2147483648      // вне диапазона
-2147483648
-2147483649     // вне диапазона
3.14
"""
    }
    
    # Создаем папки
    valid_dir = os.path.join(os.path.dirname(__file__), 'lexer', 'valid')
    invalid_dir = os.path.join(os.path.dirname(__file__), 'lexer', 'invalid')
    
    os.makedirs(valid_dir, exist_ok=True)
    os.makedirs(invalid_dir, exist_ok=True)
    
    # Создаем valid тесты
    print("Создание valid тестов (18 шт)...")
    for filename, content in valid_tests.items():
        filepath = os.path.join(valid_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"  {filename}")
    
    # Создаем invalid тесты
    print("\nСоздание invalid тестов (12 шт)...")
    for filename, content in invalid_tests.items():
        filepath = os.path.join(invalid_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"  {filename}")
    
    total = len(valid_tests) + len(invalid_tests)
    print(f"\nВсего создано: {len(valid_tests)} valid + {len(invalid_tests)} invalid = {total} тестов")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create":
        create_test_files()
    else:
        runner = TestRunner()
        runner.run_all_tests()
        
        print("\nИспользование:")
        print("  python tests/test_runner.py           # запустить тесты")
        print("  python tests/test_runner.py --create  # создать тесты")