#!/usr/bin/env python3
"""
Test Runner для Lexer
20 валидных тестов (сравнение с .expected) + 10 невалидных (проверка ошибок) = 30 тестов
"""

import sys
import os
import glob

# путь к src
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
        self.total_valid = 20
        self.total_invalid = 10
    
    def print_header(self, text):
        print(f"\n{text}")
    
    # ВАЛИДНЫЕ ТЕСТЫ (сравнение с файлами) 
    def run_valid_test(self, src_file):
        """Запускает валидный тест и сравнивает с .expected файлом"""
        test_name = os.path.basename(src_file).replace('.src', '')
        expected_file = os.path.join(self.expected_dir, f"{test_name}.expected")
        output_file = os.path.join(self.output_dir, f"{test_name}.output")
        
        # Проверяем наличие ожидаемого файла
        if not os.path.exists(expected_file):
            print(f"   {test_name} - нет файла {test_name}.expected (запусти --generate)")
            self.failed += 1
            return False
        
        # Читаем исходный код
        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Запускаем сканер
        scanner = Scanner(source)
        
        # Проверяем, что нет ошибок (для валидных тестов)
        if scanner.errors:
            print(f"   {test_name} - найдены ошибки в валидном коде:")
            for err in scanner.errors[:3]:
                print(f"       {err}")
            self.failed += 1
            return False
        
        # Генерируем вывод
        output_lines = []
        for token in scanner.tokens:
            if token.literal_value is not None:
                output_lines.append(f"{token.line}:{token.column} {token.type.value} \"{token.lexeme}\" {token.literal_value}")
            else:
                output_lines.append(f"{token.line}:{token.column} {token.type.value} \"{token.lexeme}\"")
        
        # Сохраняем вывод
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        
        # Читаем ожидаемый вывод
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
            
            # Показываем различия
            min_len = min(len(expected_lines), len(output_lines))
            for i in range(min_len):
                if expected_lines[i] != output_lines[i]:
                    print(f"      Различие в строке {i+1}:")
                    print(f"        Ожидалось: {expected_lines[i]}")
                    print(f"        Получено:  {output_lines[i]}")
                    break
            else:
                if len(expected_lines) != len(output_lines):
                    print(f"      Разное количество строк")
            
            self.failed += 1
            return False
    
    #  НЕВАЛИДНЫЕ ТЕСТЫ (проверка ошибок)
    
    def run_invalid_test(self, src_file):
        """Запускает невалидный тест - проверяет наличие ошибок"""
        test_name = os.path.basename(src_file).replace('.src', '')
        
        # Читаем исходный код
        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Запускаем сканер
        scanner = Scanner(source)
        
        # Для невалидных тестов ДОЛЖНЫ быть ошибки
        if scanner.errors:
            error_count = len(scanner.errors)
            print(f"   {test_name} (найдено ошибок: {error_count})")
            self.passed += 1
            return True
        else:
            print(f"   {test_name} - ожидались ошибки, но их нет")
            self.failed += 1
            return False
    
    # ГЕНЕРАЦИЯ ОЖИДАЕМЫХ ФАЙЛОв
    
    def generate_expected_file(self, src_file):
        """Генерирует .expected файл для валидного теста"""
        test_name = os.path.basename(src_file).replace('.src', '')
        expected_file = os.path.join(self.expected_dir, f"{test_name}.expected")
        
        # Читаем исходный код
        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()
        
        # Запускаем сканер
        scanner = Scanner(source)
        
        # ЕСЛИ ЕСТЬ ОШИБКИ - НЕ ГЕНЕРИРУЕМ ФАЙЛ!
        if scanner.errors:
            print(f"   {test_name} - В КОДЕ ЕСТЬ ОШИБКИ! Файл НЕ создан:")
            for err in scanner.errors:
                print(f"      • {err}")
            return False
        
        # Генерируем ожидаемый вывод (только если нет ошибок)
        expected_lines = []
        expected_lines.append(f"# Test: {test_name}")
        expected_lines.append(f"# Generated: автоматически")
        
        for token in scanner.tokens:
            if token.literal_value is not None:
                expected_lines.append(f"{token.line}:{token.column} {token.type.value} \"{token.lexeme}\" {token.literal_value}")
            else:
                expected_lines.append(f"{token.line}:{token.column} {token.type.value} \"{token.lexeme}\"")
        
        # Записываем файл
        with open(expected_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(expected_lines))
        
        print(f"   {test_name}.expected создан (ошибок нет)")
        return True
    
    def generate_all_expected(self):
        """Генерирует все .expected файлы для валидных тестов"""
        self.print_header("ГЕНЕРАЦИЯ ОЖИДАЕМЫХ ФАЙЛОВ (20 шт)")
        
        valid_files = sorted(glob.glob(os.path.join(self.valid_dir, '*.src')))
        
        if len(valid_files) != 20:
            print(f"    Найдено {len(valid_files)} валидных тестов, ожидалось 20")
        
        generated = 0
        for src_file in valid_files:
            if self.generate_expected_file(src_file):
                generated += 1
        
        print(f"\n Сгенерировано {generated} из {len(valid_files)} файлов в {self.expected_dir}")
    
    # ЗАПУСК ВСЕХ ТЕСТОВ
    
    def run_all_tests(self):
        """Запускает все 30 тестов"""
        
        # Сбрасываем счетчики
        self.passed = 0
        self.failed = 0
        
        # ВАЛИДНЫЕ ТЕСТЫ
        self.print_header("ВАЛИДНЫЕ ТЕСТЫ (20 шт) - сравнение с .expected")
        valid_files = sorted(glob.glob(os.path.join(self.valid_dir, '*.src')))
        
        if len(valid_files) != 20:
            print(f"    Найдено {len(valid_files)} валидных тестов, должно быть 20")
            print(f"     Запусти: python tests/test_runner.py --create")
        
        for test_file in valid_files:
            self.run_valid_test(test_file)
        
        # НЕВАЛИДНЫЕ ТЕСТЫ
        self.print_header("НЕВАЛИДНЫЕ ТЕСТЫ (10 шт) - проверка наличия ошибок")
        invalid_files = sorted(glob.glob(os.path.join(self.invalid_dir, '*.src')))
        
        if len(invalid_files) != 10:
            print(f"    Найдено {len(invalid_files)} невалидных тестов, должно быть 10")
            print(f"     Запусти: python tests/test_runner.py --create")
        
        for test_file in invalid_files:
            self.run_invalid_test(test_file)
        
        # ===== ИТОГИ =====
        self.print_header("РЕЗУЛЬТАТЫ")
        print(f"  Всего тестов: 30 (20 valid + 10 invalid)")
        print(f"   Пройдено: {self.passed}")
        print(f"   Провалено: {self.failed}")
        
        if self.failed == 0:
            print("\n   ВСЕ 30 ТЕСТОВ ПРОЙДЕНЫ!")
            return True
        else:
            print(f"\n    Провалено: {self.failed} из 30")
            return False

#СОЗДАНИЕ ТЕСТОВЫХ ФАЙЛОВ

def create_test_files():
    """Создает 20 валидных и 10 невалидных тестов"""
    
    valid_dir = os.path.join(os.path.dirname(__file__), 'lexer', 'valid')
    invalid_dir = os.path.join(os.path.dirname(__file__), 'lexer', 'invalid')
    
    os.makedirs(valid_dir, exist_ok=True)
    os.makedirs(invalid_dir, exist_ok=True)

    #20 ВАЛИДНЫХ ТЕСТОВ
    valid_tests = {
        '01_identifiers.src': """
// Идентификаторы
counter
temp
result
_private
value123
""",
        '02_numbers.src': """
// Целые числа в допустимом диапазоне
0
42
1000
-5
2147483647
-2147483648
""",
        '03_floats.src': """
// Числа с плавающей точкой
3.14
0.5
10.0
-0.001
999.999
""",
        '04_keywords.src': """
// Ключевые слова
int float bool
if else while for
return true false
void struct fn
""",
        '05_operators_arith.src': """
// Арифметические операторы
+ - * / %
x + y
a - b
c * d
e / f
g % h
""",
        '06_operators_compare.src': """
// Операторы сравнения
== != < > <= >=
x == y
a != b
c < d
e > f
g <= h
i >= j
""",
        '07_operators_logical.src': """
// Логические операторы
&& || !
x && y
a || b
!flag
""",
        '08_operators_assign.src': """
// Операторы присваивания
= += -= *= /=
x = 42
y += 10
z -= 5
w *= 2
v /= 3
""",
        '09_delimiters.src': """
// Разделители
( ) { } [ ] ; , :
fn main() {
    int x = 42;
    int[10] arr;
    return x;
}
""",
        '10_comments.src': """
// Однострочный комментарий
int x = 42; // комментарий

/* Многострочный
   комментарий */
int y = 99;
""",
        '11_nested_comments.src': """
/* Внешний комментарий
   /* Вложенный комментарий */
   еще текст */
int x = 42;
""",
        '12_strings.src': """
// Строковые литералы
"hello"
"hello world"
""
"special !@#$%"
"line1line2"
"simple string"
""",
        '13_expressions.src': """
// Выражения
x + y * 2
(a + b) * (c - d)
x > 10 && y < 20
counter += 1
""",
        '14_functions.src': """
// Функции
fn main() {
    return 0;
}
fn add(a int, b int) int {
    return a + b;
}
""",
        '15_conditionals.src': """
// Условные операторы
if (x > 0) {
    return x;
} else {
    return -x;
}
""",
        '16_loops.src': """
// Циклы
while (i < 10) {
    i = i + 1;
}
for (i = 0; i < 10; i = i + 1) {
    print(i);
}
""",
        '17_variables.src': """
// Переменные
int counter;
float price = 99.99;
bool flag = true;
int x, y, z;
""",
        '18_types.src': """
// Типы данных
int i = 42;
float f = 3.14;
bool b = true;
void test() {}
""",
        '19_booleans.src': """
// Булевы значения
true
false
if (true) {}
while (false) {}
return true;
""",
        '20_all_features.src': """
// Все вместе
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
    
    # 10 НЕВАЛИДНЫХ ТЕСТОВ
    invalid_tests = {
        '01_invalid_char.src': """
// Недопустимые символы
@invalid
#invalid
$invalid
`invalid
""",
        '02_unterminated_string.src': """
// Незакрытая строка
"unterminated string
int x = 42;
""",
        '03_unterminated_comment.src': """
// Незакрытый комментарий
int x = 42;
/* этот комментарий
   никогда не закрывается
int y = 99;
""",
        '04_malformed_number.src': """
// Неправильные числа
123.456.789
.123
123.
12.34.56
""",
        '05_out_of_range.src': """
// Числа вне допустимого диапазона
2147483648      // на 1 больше максимального
-2147483649     // на 1 меньше минимального
9999999999      // очень большое
""",
        '06_invalid_identifier.src': """
// Неправильные идентификаторы
123abc
a@b
a#b
a$b
""",
        '07_missing_quote.src': """
// Отсутствующие кавычки
"hello
world"
"test
""",
        '08_invalid_operator.src': """
// Неправильные операторы
x ^ y
x ~ y
x \ y
""",
        '09_empty_comment.src': """
// Пустые комментарии
/**/
/* */
///
/*/*/
""",
        '10_mixed_errors.src': """
// Смешанные ошибки
int @x = 42;
float 123.456.789;
"unterminated
/* незакрытый комментарий
"""
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