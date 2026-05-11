# MiniCompiler Project

Учебный проект по созданию компилятора (Спринт 1 - Лексический анализатор)

## Описание

Этот проект реализует первую часть компилятора - лексический анализатор (сканер).
Он преобразует исходный код на упрощенном C-подобном языке в последовательность токенов.

## Структура проекта
compiler-project/
├── src/ # Исходный код
│ ├── lexer/ # Лексический анализатор (Sprint 1)
│ │ ├── scanner.py # Сканер токенов
│ │ ├── token.py # Определения типов токенов
│ │ └── init.py
│ │
│ ├── parser/ # Синтаксический анализатор (Sprint 2)
│ │ ├── parser.py # Рекурсивный нисходящий парсер
│ │ ├── ast.py # Классы узлов AST
│ │ ├── grammar.txt # Формальная грамматика EBNF
│ │ └── init.py
│ │
│ ├── utils/ # Вспомогательные утилиты
│ │ ├── ast_printer.py # Pretty-print AST
│ │ ├── ast_dot.py # Генерация DOT для Graphviz
│ │ └── init.py
│ │
│ └── main.py # Точка входа
│
├── tests/ # Тесты
│ ├── lexer/ # Тесты лексера (Sprint 1)
│ │ ├── valid/ # 20 валидных тестов
│ │ ├── invalid/ # 10 невалидных тестов
│ │ └── expected/ # Эталонные токены
│ │
│ ├── parser/ # Тесты парсера (Sprint 2)
│ │ ├── valid/ # 11 валидных тестов
│ │ │ ├── expressions/ # Выражения
│ │ │ ├── statements/ # Операторы
│ │ │ ├── declarations/ # Объявления
│ │ │ └── full_programs/ # Полные программы
│ │ ├── invalid/ # 2 невалидных теста
│ │ │ └── syntax_errors/ # Синтаксические ошибки
│ │ ├── expected/ # эталонные файлы
│ │ │ ├── valid_* # AST для валидных тестов
│ │ │ └── invalid_* # Ожидаемые ошибки
│ │ └── output/ # Результаты тестов
│ │
│ ├── test_runner.py # Раннер тестов лексера
│ └── test_parser.py # Раннер тестов парсера
│
├── examples/ # Примеры программ
│ ├── test1.src #1sp
│ ├── test2.src #1sp
│ └── test3.src #2sp
│
└── docs/ # Документация
└── language_spec.md # Спецификация языка


## Установка и запуск

1. Запуск тестов:
Создание тестов (один раз)
python tests/test_runner.py --generate

2. запуск тестов лексера:

python tests/test_runner.py

3. запуск конкретного примера:
python tests/test_scanner.py

## Sprint 2 - Синтаксический анализатор (Parser)
python src/main.py parse examples/test3.src

# Разные форматы вывода AST
python src/main.py parse --format text examples/test3.src
python src/main.py parse --format json examples/test3.src

# Сохранить AST в файл
python src/main.py parse --output ast.txt examples/test3.src


# Запустить тесты парсера
python -m pytest tests/parser/ -v

# Создание DOT файла
python src/main.py parse examples/test.src --format dot --output ast.dot

# Создание PNG файла
dot -Tpng ast.dot -o ast.png

# Просмотр
start ast.png


## Sprint 3 - Семантический анализатор
# Валидные тесты
# 1. Простая функция
python -c "open('test1.src', 'w', encoding='utf-8').write('fn main() -> int {\n    return 42;\n}')"
echo 1. Простая функция:
python src\main.py check test1.src

# 2. Переменные и арифметика
python -c "open('test2.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 10;\n    int y = 20;\n    int z = x + y;\n    return z;\n}')"
echo 2. Переменные и арифметика:
python src\main.py check test2.src

# 3. Функции и вызовы
python -c "open('test3.src', 'w', encoding='utf-8').write('fn add(int a, int b) -> int {\n    return a + b;\n}\nfn main() -> int {\n    return add(5, 3);\n}')"
echo 3. Функции и вызовы:
python src\main.py check test3.src

# 4. Вложенные блоки
python -c "open('test4.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 10;\n    if (x > 5) {\n        int y = 20;\n        x = x + y;\n    }\n    return x;\n}')"
echo 4. Вложенные блоки:
python src\main.py check test4.src

# 5. Условия
python -c "open('test5.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 5;\n    if (x == 5) {\n        return 1;\n    } else {\n        return 0;\n    }\n}')"
echo 5. Условия:
python src\main.py check test5.src

# 6. Сложные выражения
python -c "open('test6.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int a = 5 + 3 * 2;\n    int b = (10 - 4) / 2;\n    int c = a * b + 1;\n    return c;\n}')"
echo 6. Сложные выражения:
python src\main.py check test6.src

# 7. Цикл while
python -c "open('test7.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int i = 0;\n    int sum = 0;\n    while (i < 10) {\n        sum = sum + i;\n        i = i + 1;\n    }\n    return sum;\n}')"
echo 7. Цикл while:
python src\main.py check test7.src

# 8. Цикл for
python -c "open('test8.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int sum = 0;\n    for (int i = 0; i < 5; i = i + 1) {\n        sum = sum + i;\n    }\n    return sum;\n}')"
echo 8. Цикл for:
python src\main.py check test8.src

# 9. Логические операции
python -c "open('test9.src', 'w', encoding='utf-8').write('fn main() -> int {\n    bool a = true;\n    bool b = false;\n    bool c = a && b;\n    bool d = a || b;\n    if (c == false && d == true) {\n        return 1;\n    }\n    return 0;\n}')"
echo 9. Логические операции:
python src\main.py check test9.src

# 10. Разные типы
python -c "open('test10.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 42;\n    float y = 3.14;\n    bool z = true;\n    return x;\n}')"
echo 10. Разные типы:
python src\main.py check test10.src


# Невалидные тесты
# 1. Необъявленная переменная
python -c "open('e1.src', 'w', encoding='utf-8').write('fn main() -> int {\n    x = 10;\n    return x;\n}')"
echo 1. Необъявленная переменная:
python src\main.py check e1.src

# 2. Несоответствие типов (int = string)
python -c "open('e2.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = \"hello\";\n    return x;\n}')"
echo 2. Несоответствие типов:
python src\main.py check e2.src

# 3. Дублирующаяся функция
python -c "open('e3.src', 'w', encoding='utf-8').write('fn foo() -> int { return 1; }\nfn foo() -> int { return 2; }\nfn main() -> int { return 0; }')"
echo 3. Дублирующаяся функция:
python src\main.py check e3.src

# 4. Неправильное количество аргументов
python -c "open('e4.src', 'w', encoding='utf-8').write('fn add(int a, int b) -> int { return a + b; }\nfn main() -> int { return add(5); }')"
echo 4. Неправильное количество аргументов:
python src\main.py check e4.src

# 5. Неправильный тип условия (if)
python -c "open('e5.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 5;\n    if (x) {\n        return 1;\n    }\n    return 0;\n}')"
echo 5. Неправильный тип условия (if):
python src\main.py check e5.src

# 6. Неправильный тип возврата
python -c "open('e6.src', 'w', encoding='utf-8').write('fn main() -> int {\n    return true;\n}')"
echo 6. Неправильный тип возврата:
python src\main.py check e6.src

# 7. Вызов не-функции
python -c "open('e7.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 10;\n    return x();\n}')"
echo 7. Вызов не-функции:
python src\main.py check e7.src

# 8. Неправильный тип аргумента
python -c "open('e8.src', 'w', encoding='utf-8').write('fn add(int a, int b) -> int { return a + b; }\nfn main() -> int { return add(true, 5); }')"
echo 8. Неправильный тип аргумента:
python src\main.py check e8.src

# 9. Дублирующаяся переменная
python -c "open('e9.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 10;\n    int x = 20;\n    return x;\n}')"
echo 9. Дублирующаяся переменная:
python src\main.py check e9.src

# 10. Использование переменной вне области
python -c "open('e10.src', 'w', encoding='utf-8').write('fn main() -> int {\n    if (true) {\n        int x = 10;\n    }\n    return x;\n}')"
echo 10. Использование переменной вне области:
python src\main.py check e10.src

# 11. Неправильный тип в while
python -c "open('e11.src', 'w', encoding='utf-8').write('fn main() -> int {\n    int x = 5;\n    while (x) {\n        x = x - 1;\n    }\n    return x;\n}')"
echo 11. Неправильный тип в while:
python src\main.py check e11.src

# 12. Return с значением в void функции
python -c "open('e12.src', 'w', encoding='utf-8').write('fn foo() -> void {\n    return 42;\n}\nfn main() -> int { return 0; }')"
echo 12. Return с значением в void функции:
python src\main.py check e12.src

# ТАБЛИЦА СИМВОЛОВ
echo Программа с несколькими функциями:
python -c "open('sym.src', 'w', encoding='utf-8').write('fn add(int a, int b) -> int { return a + b; }\nfn sub(int a, int b) -> int { return a - b; }\nfn main() -> int { return add(5, 3); }')"
python src\main.py check --symbols sym.src

# Юнит-тесты
python -m unittest tests.test_semantic -v
python tests\test_semantic_integration.py //конкретика по тестам
# Очистка
del test.src error.src

