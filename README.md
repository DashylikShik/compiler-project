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
│ │ ├── expected/ # 13 эталонных файлов
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
python src/main.py parse --format dot examples/test3.src
python src/main.py parse --format json examples/test3.src

# Сохранить AST в файл
python src/main.py parse --output ast.txt examples/test3.src

# Запустить тесты парсера
python src/main.py test-parser
