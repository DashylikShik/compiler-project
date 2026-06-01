# MiniCompiler Project

Учебный проект по созданию компилятора

## Структура проекта
compiler-project/
├── src/                              # Исходный код
│   ├── lexer/                        # Sprint 1: Лексический анализатор
│   │   ├── scanner.py                # Сканер токенов
│   │   ├── token.py                  # Определения типов токенов
│   │   └── __init__.py
│   │
│   ├── parser/                       # Sprint 2: Синтаксический анализатор
│   │   ├── parser.py                 # Рекурсивный нисходящий парсер
│   │   ├── ast.py                    # Классы узлов AST
│   │   ├── grammar.txt               # Формальная грамматика EBNF
│   │   └── __init__.py
│   │
│   ├── semantic/                     # Sprint 3: Семантический анализатор
│   │   ├── analyzer.py               # Семантический анализ AST
│   │   ├── symbol_table.py           # Иерархическая таблица символов
│   │   ├── type_system.py            # Система типов и проверка совместимости
│   │   ├── errors.py                 # Классы семантических ошибок
│   │   └── __init__.py
│   │
│   ├── ir/                           # Sprint 4: Промежуточное представление
│   │   ├── ir_instructions.py        # Определения инструкций IR
│   │   ├── ir_generator.py           # Генератор IR из AST
│   │   ├── ir_printer.py             # Вывод в форматах (text/dot/json/html)
│   │   ├── basic_block.py            # Базовые блоки и CFG
│   │   └── __init__.py
│   │
│   ├── utils/                        # Вспомогательные утилиты
│   │   ├── ast_printer.py            # Pretty-print AST
│   │   ├── ast_dot.py                # Генерация DOT для Graphviz
│   │   └── __init__.py
│   │
│   └── main.py                       # Точка входа (все спринты)
│
├── tests/                            # Тесты
│   ├── lexer/                        # Sprint 1: Тесты лексера
│   │   ├── valid/                    # 20 валидных тестов
│   │   ├── invalid/                  # 10 невалидных тестов
│   │   ├── expected/                 # Эталонные токены
│   │   └── output/                   # Результаты тестов
│   │
│   ├── parser/                       # Sprint 2: Тесты парсера
│   │   ├── valid/                    # Валидные тесты
│   │   │   ├── expressions/          # Выражения
│   │   │   ├── statements/           # Операторы
│   │   │   ├── declarations/         # Объявления
│   │   │   └── full_programs/        # Полные программы
│   │   ├── invalid/                  # Невалидные тесты
│   │   │   └── syntax_errors/        # Синтаксические ошибки
│   │   ├── expected/                 # Эталонные файлы
│   │   │   ├── valid_*               # AST для валидных тестов
│   │   │   └── invalid_*             # Ожидаемые ошибки
│   │   └── output/                   # Результаты тестов
│   │
│   ├── semantic/                     # Sprint 3: Тесты семантики
│   │   ├── valid/                    # Валидные семантические тесты
│   │   ├── invalid/                  # Невалидные тесты (ошибки)
│   │   ├── expected/                 # Эталонные результаты
│   │   └── output/                   # Результаты тестов
│   │
│   ├── ir/                           # Sprint 4: Тесты IR
│   │   ├── generation/               # Тесты генерации IR
│   │   │   ├── expressions/          # Арифметические выражения
│   │   │   │   ├── arithmetic.src
│   │   │   │   └── expected/
│   │   │   ├── control_flow/         # Управление потоком (if/while)
│   │   │   │   ├── if_statement.src
│   │   │   │   ├── while_loop.src
│   │   │   │   └── expected/
│   │   │   └── functions/            # Функции и вызовы
│   │   │       ├── call.src
│   │   │       ├── multiple.src
│   │   │       └── expected/
│   │   ├── validation/               # Валидационные проверки
│   │   ├── test_runner.py            # Основные тесты IR (14 тестов)
│   │   ├── test_golden.py            # Golden тесты (7 тестов)
│   │   └── __init__.py
│   │
│   ├── test_runner.py                # Раннер тестов лексера
│   ├── test_parser.py                # Раннер тестов парсера
│   ├── test_semantic.py              # Юнит-тесты семантики
│   └── __init__.py
│
├── examples/                         # Примеры программ
│   ├── test1.src
│   ├── test2.src
│   ├── test3.src
│   └── factorial.src                 # Пример с рекурсией
│
├── docs/                             # Документация
│   ├── language_spec.md              # Спецификация языка
│   └── ir_spec.md                    # Спецификация IR
│
├── .gitignore                        # Исключения Git
├── README.md                         # Документация проекта
├── setup.py                          # Установка пакета


## Установка и запуск

# Путь к проекту:
dashylik@HOME-PC:/mnt/c/Windows/System32$ cd /mnt/c
dashylik@HOME-PC:/mnt/c$ cd Users
dashylik@HOME-PC:/mnt/c/Users$ cd Пользователь
dashylik@HOME-PC:/mnt/c/Users/Пользователь$ cd Desktop
dashylik@HOME-PC:/mnt/c/Users/Пользователь/Desktop$ cd compiler-project\


1. Запуск тестов:
Создание тестов (один раз)
python3 tests/test_runner.py --generate

2. запуск тестов лексера:

python3 tests/test_runner.py

3. запуск конкретного примера:
python3 tests/test_scanner.py

## Sprint 2 - Синтаксический анализатор (Parser)
python3 src/main.py parse examples/test3.src

# Разные форматы вывода AST
python3 src/main.py parse --format text examples/test3.src
python3 src/main.py parse --format json examples/test3.src

# Сохранить AST в файл
python3 src/main.py parse --output ast.txt examples/test3.src


# Запустить тесты парсера
python3 -m pytest tests/parser/ -v

# Создание DOT файла
python3 src/main.py parse examples/test.src --format dot --output ast.dot

# Создание PNG файла
dot -Tpng ast.dot -o ast.png

# Просмотр
start ast.png


## Sprint 3 - Семантический анализатор
# Валидные тесты
# 1. Простая функция
python3 -c "open('test1.src', 'w', encoding='utf-8').write('fn main() -> int {\n    return 42;\n}')"
echo 1. Простая функция:
python3 src\main.py check test1.src

# 2. Переменные и арифметика
python3 -c "open('test2.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 10;\n    int y = 20;\n    int z = x + y;\n    return z;\n}')"
echo 2. Переменные и арифметика:
python3 src\main.py check test2.src

# 3. Функции и вызовы
python3 -c "open('test3.src', 'w', encoding='utf-8').write('fn add(int a, int b) -> int {\n    return a + b;\n}\nfn main() -> int {\n    return add(5, 3);\n}')"
echo 3. Функции и вызовы:
python3 src\main.py check test3.src

# 4. Вложенные блоки
python3 -c "open('test4.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 10;\n    if (x > 5) {\n        int y = 20;\n        x = x + y;\n    }\n    return x;\n}')"
echo 4. Вложенные блоки:
python3 src\main.py check test4.src

# 5. Условия
python3 -c "open('test5.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 5;\n    if (x == 5) {\n        return 1;\n    } else {\n        return 0;\n    }\n}')"
echo 5. Условия:
python3 src\main.py check test5.src

# 6. Сложные выражения
python3 -c "open('test6.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int a = 5 + 3 * 2;\n    int b = (10 - 4) / 2;\n    int c = a * b + 1;\n    return c;\n}')"
echo 6. Сложные выражения:
python3 src\main.py check test6.src

# 7. Цикл while
python3 -c "open('test7.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int i = 0;\n    int sum = 0;\n    while (i < 10) {\n        sum = sum + i;\n        i = i + 1;\n    }\n    return sum;\n}')"
echo 7. Цикл while:
python3 src\main.py check test7.src

# 8. Цикл for
python3 -c "open('test8.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int sum = 0;\n    for (int i = 0; i < 5; i = i + 1) {\n        sum = sum + i;\n    }\n    return sum;\n}')"
echo 8. Цикл for:
python3 src\main.py check test8.src

# 9. Логические операции
python3 -c "open('test9.src', 'w', encoding='utf-8').write('fn main() -> int {\n    bool a = true;\n    bool b = false;\n    bool c = a && b;\n    bool d = a || b;\n    if (c == false && d == true) {\n        return 1;\n    }\n    return 0;\n}')"
echo 9. Логические операции:
python3 src\main.py check test9.src

# 10. Разные типы
python3 -c "open('test10.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 42;\n    float y = 3.14;\n    bool z = true;\n    return x;\n}')"
echo 10. Разные типы:
python3 src\main.py check test10.src


# Невалидные тесты
# 1. Необъявленная переменная
python3 -c "open('e1.src', 'w', encoding='utf-8').write('fn main() -> int {\n    x = 10;\n    return x;\n}')"
echo 1. Необъявленная переменная:
python3 src\main.py check e1.src

# 2. Несоответствие типов (int = string)
python3 -c "open('e2.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = \"hello\";\n    return x;\n}')"
echo 2. Несоответствие типов:
python3 src\main.py check e2.src

# 3. Дублирующаяся функция
python3 -c "open('e3.src', 'w', encoding='utf-8').write('fn foo() -> int { return 1; }\nfn foo() -> int { return 2; }\nfn main() -> int { return 0; }')"
echo 3. Дублирующаяся функция:
python3 src\main.py check e3.src

# 4. Неправильное количество аргументов
python3 -c "open('e4.src', 'w', encoding='utf-8').write('fn add(int a, int b) -> int { return a + b; }\nfn main() -> int { return add(5); }')"
echo 4. Неправильное количество аргументов:
python3 src\main.py check e4.src

# 5. Неправильный тип условия (if)
python3 -c "open('e5.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 5;\n    if (x) {\n        return 1;\n    }\n    return 0;\n}')"
echo 5. Неправильный тип условия (if):
python3 src\main.py check e5.src

# 6. Неправильный тип возврата
python3 -c "open('e6.src', 'w', encoding='utf-8').write('fn main() -> int {\n    return true;\n}')"
echo 6. Неправильный тип возврата:
python3 src\main.py check e6.src

# 7. Вызов не-функции
python3 -c "open('e7.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 10;\n    return x();\n}')"
echo 7. Вызов не-функции:
python3 src\main.py check e7.src

# 8. Неправильный тип аргумента
python3 -c "open('e8.src', 'w', encoding='utf-8').write('fn add(int a, int b) -> int { return a + b; }\nfn main() -> int { return add(true, 5); }')"
echo 8. Неправильный тип аргумента:
python3 src\main.py check e8.src

# 9. Дублирующаяся переменная
python3 -c "open('e9.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 10;\n    int x = 20;\n    return x;\n}')"
echo 9. Дублирующаяся переменная:
python3 src\main.py check e9.src

# 10. Использование переменной вне области
python3 -c "open('e10.src', 'w', encoding='utf-8').write('fn main() -> int {\n    if (true) {\n        int x = 10;\n    }\n    return x;\n}')"
echo 10. Использование переменной вне области:
python3 src\main.py check e10.src

# 11. Неправильный тип в while
python3 -c "open('e11.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 5;\n    while (x) {\n        x = x - 1;\n    }\n    return x;\n}')"
echo 11. Неправильный тип в while:
python3 src\main.py check e11.src

# 12. Return с значением в void функции
python3 -c "open('e12.src', 'w', encoding='utf-8').write('fn foo() -> void {\n    return 42;\n}\nfn main() -> int { return 0; }')"
echo 12. Return с значением в void функции:
python3 src\main.py check e12.src

# ТАБЛИЦА СИМВОЛОВ
echo Программа с несколькими функциями:
python3 -c "open('sym.src', 'w', encoding='utf-8').write('fn add(int a, int b) -> int { return a + b; }\nfn sub(int a, int b) -> int { return a - b; }\nfn main() -> int { return add(5, 3); }')"
python3 src\main.py check --symbols sym.src

# Юнит-тесты
python3 -m unittest tests.test_semantic -v
python3 tests\test_semantic_integration.py //конкретика по тестам
# Очистка
del test.src error.src


## Sprint 4: Intermediate Representation (IR)

# 1 Проверка базовой генерации IR
python3 src/main.py ir tests/ir/generation/expressions/arithmetic.src

# 2 Проверка всех форматов
# Текстовый формат
python3 src/main.py ir test.src

# DOT формат
python3 src/main.py ir --format dot test.src

# JSON формат
python3 src/main.py ir --format json test.src

# HTML формат
python3 src/main.py ir --format html test.src --output test.html

# 3 Проверка сложного примера (факториал)
python3 -c "open('fact.src','w').write('fn fact(int n)->int{if(n<=1){return 1;}else{return n*fact(n-1);}}')"
python3 src/main.py ir fact.src


# 4. Показать статистику
python3 src/main.py ir --verbose tests/ir/generation/expressions/arithmetic.src

# 5. Запустить все тесты
python3 tests/ir/test_runner.py

# 6. Запустить golden тесты
python3 tests/ir/test_golden.py


## Sprint 5: x86-64 Assembly Generation

# Тест 1: Простая функция
python3 src\main.py compile test1.src --verbose

# Тест 2: Арифметика
python3 src\main.py compile tests\codegen\valid\arithmetic_ops\add.src

# Тест 3: If условие
python3 src\main.py compile tests\codegen\valid\control_flow\if.src

# Тест 4: Вызов функции
python3 src\main.py compile tests\codegen\valid\function_calls\call.src


python3 src\main.py compile test1.src
python3 src\main.py compile test1.src --output program.asm
python3 src\main.py compile test1.src --verbose
type test1.asm

# Создаем тест с функцией
python3 -c "open('test_call.src', 'w', encoding='utf-8').write('fn add(int a, int b) -> int { return a + b; }\nfn main() -> int { return add(5, 3); }')"

# Компилируем
python3 src/main.py compile test_call.src

# Смотрим ассемблер
type test_call.asm

# Тест 1: Несуществующая функция(инвалидные тесты)
python3 -c "open('tests/codegen/invalid/assembly_errors/undefined_function.src','w',encoding='utf-8').write('fn main() -> int { return unknown(); }')"
python3 src/main.py compile tests/codegen/invalid/assembly_errors/undefined_function.src

# Тест 2: Неправильный тип (строка вместо числа)
python3 -c "open('tests/codegen/invalid/runtime_errors/type_error.src','w',encoding='utf-8').write('fn main() -> int { int x = \"hello\"; return x; }')"
python3 src/main.py compile tests/codegen/invalid/runtime_errors/type_error.src

# Запуск тестов
python3 tests/codegen/test_runner.py


## Sprint 6: Control flow and short-circuit evaluition
# Сначала посмотреть IR
python3 src/main.py ir tests/control_flow/valid/conditionals/if_else.src

# Потом скомпилировать в ассемблер
python3 src/main.py compile tests/control_flow/valid/conditionals/if_else.src
cd C:\Users\Пользователь\Desktop\compiler-project

# While loop тест
python3 src/main.py compile tests/control_flow/valid/loops/while_loop.src --verbose

# For loop тест
python3 src/main.py compile tests/control_flow/valid/loops/for_loop.src --verbose

# Logical AND тест
python3 src/main.py compile tests/control_flow/valid/logical_ops/short_circuit_and.src --verbose

# Precedence тест
python3 src/main.py compile tests/control_flow/valid/complex_expressions/precedence.src --verbose

# Первый запуск - сгенерирует expected файлы
python3 tests\control_flow\test_golden.py

# Второй запуск - сравнит с expected
python3 tests\control_flow\test_golden.py


# 1. Переход в папку проекта
cd C:\Users\Пользователь\Desktop\compiler-project

# 2. Запуск Visual Studio окружение (из папки проекта)
"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"

# 3. Теперь слинк
link test_short.obj /entry:main /subsystem:console /out:test_short.exe

# 4. Запуск программы
test_short.exe

# 5. код возврата
echo %errorlevel%


# 2. Компилируем в ассемблер
python3 src/main.py compile test_arith.src --output test_arith.asm

# 3. Ассемблируем
nasm -f win64 test_arith.asm -o test_arith.obj

# 4. Линкуем в exe
link test_arith.obj /entry:main /subsystem:console /out:test_arith.exe

# 5. Запускаем
test_arith.exe

# 6. Смотрим код возврата
echo %errorlevel%

# Тест 1: простое возвращение числа
python3 -c "open('test_simple.src', 'w', encoding='utf-8').write('fn main() -> int { return 42; }')"
python3 src/main.py compile test_simple.src --output test_simple.asm
nasm -f win64 test_simple.asm -o test_simple.obj
link test_simple.obj /entry:main /subsystem:console /out:test_simple.exe
test_simple.exe
echo %errorlevel%

## Sprint 7:

# TEST-1: Тесты массивов
python3 -c "open('tests/array/valid/01_declaration.src','w').write('fn main() -> int { int arr[5]; return 0; }')"
python3 -c "open('tests/array/valid/02_initialized.src','w').write('fn main() -> int { int arr[3] = {1, 2, 3}; return arr[0]; }')"
python3 -c "open('tests/array/valid/03_access.src','w').write('fn main() -> int { int arr[5] = {1,2,3,4,5}; arr[2] = 10; return arr[2]; }')"
python3 -c "open('tests/array/valid/04_multidim.src','w').write('fn main() -> int { int matrix[3][4]; matrix[1][2] = 42; return matrix[1][2]; }')"
python3 -c "open('tests/array/valid/05_param.src','w').write('fn sum(int arr[], int size) -> int { int total = 0; for (int i = 0; i < size; i = i + 1) { total = total + arr[i]; } return total; }\nfn main() -> int { int arr[5] = {1,2,3,4,5}; return sum(arr, 5); }')"

echo "01_declaration:"
python3 src/main.py check tests/array/valid/01_declaration.src

Linux:
python3 src/main.py compile tests/array/valid/01_declaration.src
nasm -f elf64 tests/array/valid/01_declaration.asm -o 01_declaration.o
gcc -no-pie 01_declaration.o  -o 01_declaration
./01_declaratiom
echo $?

echo "02_initialized:"
python3 src/main.py check tests/array/valid/02_initialized.src

echo "03_access:"
python3 src/main.py check tests/array/valid/03_access.src

echo "04_multidim:"
python3 src/main.py check tests/array/valid/04_multidim.src

echo "05_param:"
python3 src/main.py check tests/array/valid/05_param.src

# TEST-2: Тесты внешних вызовов
python33 -c "open('tests/external/valid/01_printf.src','w').write('extern int printf(char* format, ...);\nfn main() -> int { printf(\"Hello World!\\n\"); return 0; }')"

python3 -c "open('tests/external/valid/02_malloc.src','w').write('extern void* malloc(int size);\nextern void free(void* ptr);\nfn main() -> int { void* ptr = malloc(4); if (ptr != 0) { free(ptr); } return 0; }')"

python3 -c "open('tests/external/valid/03_math.src','w').write('extern int pow(int x, int y);\nextern int sqrt(int x);\nfn main() -> int { int x = pow(2, 3); int y = sqrt(16); return 0; }')"

python3 -c "open('tests/external/valid/04_string.src','w').write('extern int strlen(char* str);\nextern char* strcpy(char* dest, char* src);\nfn main() -> int { char str[20]; strcpy(str, \"hello\"); int len = strlen(str); return len; }')"

echo "01_printf:"
python3 src/main.py check tests/external/valid/01_printf.src

echo "02_malloc:"
python3 src/main.py check tests/external/valid/02_malloc.src

echo "03_math:"
python3 src/main.py check tests/external/valid/03_math.src

echo "04_string:"
python3 src/main.py check tests/external/valid/04_string.src

# TEST-3: Тесты оптимизаций
python3 -c "open('tests/optimization/valid/01_folding.src', 'w', encoding='utf-8').write('fn main() -> int { int x = 2 + 3; int y = 4 * 5; return x + y; }')"
python3 -c "open('tests/optimization/valid/02_propagation.src', 'w', encoding='utf-8').write('fn main() -> int { int x = 5; int y = x; int z = y + 10; return z; }')"
python3 -c "open('tests/optimization/valid/03_dce.src', 'w', encoding='utf-8').write('fn main() -> int { int x = 5; if (1 > 2) { return 10; } return x; }')"
python3 -c "open('tests/optimization/valid/04_compare.src', 'w', encoding='utf-8').write('fn main() -> bool { return 5 > 3; }')"
python3 -c "open('tests/optimization/valid/05_logic.src', 'w', encoding='utf-8').write('fn main() -> bool { bool x = true && false; bool y = true || false; return x; }')"
python3 -c "open('tests/optimization/valid/06_mixed.src', 'w', encoding='utf-8').write('fn main() -> int { int a = 2 + 3; int b = a * 2; if (b > 10) { return 100; } else { return b; } }')"

echo "01_folding:"
python3 src/main.py compile tests/optimization/valid/01_folding.src --optimize --verbose

echo "02_propagation:"
python3 src/main.py compile tests/optimization/valid/02_propagation.src --optimize --verbose

echo "03_dce:"
python3 src/main.py compile tests/optimization/valid/03_dce.src --optimize --verbose

echo "04_compare:"
python3 src/main.py compile tests/optimization/valid/04_compare.src --optimize --verbose

echo "05_logic:"
python3 src/main.py compile tests/optimization/valid/05_logic.src --optimize --verbose

echo "06_mixed:"
python3 src/main.py compile tests/optimization/valid/06_mixed.src --optimize --verbose

# запуск тестов
sed -i 's/\r$//' run_valid_tests.py
chmod +x run_valid_tests.py
./run_valid_tests.py

python3 src/main.py check tests/array/invalid/01_out_of_bounds.src
python3 src/main.py check tests/external/invalid/01_wrong_args.src