#!/usr/bin/env python3
"""
Точка входа для компилятора
Поддерживает:
  Sprint 1: лексический анализ
  Sprint 2: синтаксический анализ + AST
  Sprint 3: семантический анализ
"""

import sys
import os
import json
import argparse

# Добавляем путь к пакетам
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(__file__))

from lexer.scanner import Scanner
from parser.parser import Parser
from utils.ast_printer import ASTPrinter
from utils.ast_dot import ASTDotGenerator
from semantic.analyzer import SemanticAnalyzer
from semantic.errors import SemanticError


def print_usage():
    """Печатает информацию об использовании"""
    print("Использование:")
    print("  compiler lex <file.src>              # Только лексический анализ (Sprint 1)")
    print("  compiler parse <file.src>             # Синтаксический анализ + AST (Sprint 2)")
    print("  compiler check <file.src>             # Семантический анализ (Sprint 3)")
    print("  compiler check --verbose <file.src>   # Семантический анализ с подробным выводом")
    print("  compiler check --symbols <file.src>   # Вывести таблицу символов")
    print("  compiler parse --format [text|dot|json] <file.src>")
    print("  compiler test                          # Запустить тесты лексера")
    print("  compiler test-parser                   # Запустить тесты парсера")
    print("  compiler test-semantic                 # Запустить тесты семантического анализа")
    print("  compiler --help                        # Показать помощь")
    return 0


def run_lexer(filename):
    """Запускает только лексический анализ (Sprint 1)"""
    if not os.path.exists(filename):
        print(f"Ошибка: файл '{filename}' не найден")
        return 1

    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()

    print(f"Анализ файла (лексический): {filename}")
    print("-" * 50)

    scanner = Scanner(source)

    for token in scanner.tokens:
        print(token)

    if scanner.errors:
        print("\nНайденные ошибки:")
        for error in scanner.errors:
            print(f"  {error}")
    else:
        print("\nОшибок не найдено")

    return 0


def run_parser(args):
    """Запускает синтаксический анализ с AST (Sprint 2)"""
    # Парсим аргументы командной строки
    format_type = "text"
    output_file = None
    filename = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--format" and i + 1 < len(args):
            format_type = args[i + 1]
            i += 2
        elif arg == "--output" and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif arg.startswith("--"):
            print(f"Неизвестная опция: {arg}")
            return 1
        else:
            filename = arg
            i += 1

    if not filename:
        print("Ошибка: укажите файл для анализа")
        return 1

    if not os.path.exists(filename):
        print(f"Ошибка: файл '{filename}' не найден")
        return 1

    # Читаем исходный файл
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()

    print(f"Анализ файла (синтаксический): {filename}")
    print("-" * 50)

    # Лексический анализ
    scanner = Scanner(source)
    if scanner.errors:
        print("Ошибки лексического анализа:")
        for error in scanner.errors:
            print(f"  {error}")
        return 1

    # Синтаксический анализ
    parser = Parser(scanner.tokens)
    try:
        ast = parser.parse()
    except Exception as e:
        print(f"Ошибка парсера: {e}")
        return 1

    if parser.errors:
        print("\nОшибки синтаксического анализа:")
        for error in parser.errors:
            print(f"  {error}")
        return 1

    # Вывод AST в запрошенном формате
    if format_type == "text":
        output = ASTPrinter.print(ast)
    elif format_type == "dot":
        output = ASTDotGenerator.generate(ast)
    elif format_type == "json":
        output = json.dumps(ast_to_dict(ast), indent=2, ensure_ascii=False)
    else:
        print(f"Неизвестный формат: {format_type}")
        return 1

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"\nAST сохранен в файл: {output_file}")
    else:
        print("\n" + output)

    return 0


def run_semantic_analysis(args):
    """Запускает семантический анализ (Sprint 3)"""
    verbose = False
    show_symbols = False
    filename = None
    output_file = None

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--verbose" or arg == "-v":
            verbose = True
            i += 1
        elif arg == "--symbols" or arg == "-s":
            show_symbols = True
            i += 1
        elif arg == "--output" and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif arg.startswith("--"):
            print(f"Неизвестная опция: {arg}")
            return 1
        else:
            filename = arg
            i += 1

    if not filename:
        print("Ошибка: укажите файл для анализа")
        return 1

    if not os.path.exists(filename):
        print(f"Ошибка: файл '{filename}' не найден")
        return 1

    # Читаем исходный файл
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()

    print(f"Анализ файла (семантический): {filename}")

    # Лексический анализ
    scanner = Scanner(source)
    if scanner.errors:
        print("Ошибки лексического анализа:")
        for error in scanner.errors:
            print(f"  {error}")
        return 1

    # Синтаксический анализ
    parser = Parser(scanner.tokens)
    try:
        ast = parser.parse()
    except Exception as e:
        print(f"Ошибка парсера: {e}")
        return 1

    if parser.errors:
        print("\nОшибки синтаксического анализа:")
        for error in parser.errors:
            print(f"  {error}")
        return 1

    # Семантический анализ
    analyzer = SemanticAnalyzer(verbose=verbose)
    analyzer.analyze(ast, source)

    # Вывод результатов
    if analyzer.has_errors():
        print("\nОшибки семантического анализа:")
        analyzer.print_errors()
        print(f"\nНайдено ошибок: {len(analyzer.get_errors())}")
    else:
        print("\nСемантических ошибок не найдено!")
    
    if verbose:
        print("\n" + "=" * 60)
        print("TYPE CHECKING RESULTS")
        print("=" * 60)
        # Здесь можно добавить вывод типов для выражений
    
    if show_symbols:
        print(analyzer.get_symbol_table().dump())
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(analyzer.get_symbol_table().dump())
        print(f"\nТаблица символов сохранена в: {output_file}")

    return 1 if analyzer.has_errors() else 0


def run_tests(test_type: str):
    """Запускает тесты"""
    if test_type == "lexer":
        test_runner = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'tests', 'test_runner.py'
        )
        if os.path.exists(test_runner):
            os.system(f'python "{test_runner}"')
        else:
            print("Ошибка: test_runner.py не найден")
    elif test_type == "parser":
        test_parser = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'tests', 'test_parser.py'
        )
        if os.path.exists(test_parser):
            os.system(f'python "{test_parser}"')
        else:
            print("Ошибка: test_parser.py не найден")
    elif test_type == "semantic":
        test_semantic = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'tests', 'test_semantic.py'
        )
        if os.path.exists(test_semantic):
            os.system(f'python "{test_semantic}"')
        else:
            print("Ошибка: test_semantic.py не найден")
    return 0


def ast_to_dict(node):
    """Конвертирует AST в словарь для JSON"""
    if node is None:
        return None
    
    # Базовая информация о узле
    result = {
        "type": node.__class__.__name__,
        "line": getattr(node, 'line', 0),
        "column": getattr(node, 'column', 0)
    }
    
    # Добавляем атрибуты в зависимости от типа узла
    if hasattr(node, 'name'):
        result["name"] = node.name
    if hasattr(node, 'value'):
        if isinstance(node.value, (str, int, float, bool)):
            result["value"] = node.value
        else:
            result["value"] = str(node.value)
    if hasattr(node, 'operator') and node.operator:
        result["operator"] = node.operator.lexeme if hasattr(node.operator, 'lexeme') else str(node.operator)
    if hasattr(node, 'return_type'):
        result["return_type"] = node.return_type
    if hasattr(node, 'literal_type'):
        result["literal_type"] = node.literal_type
    
    # Обрабатываем детей
    if hasattr(node, 'declarations') and node.declarations:
        result["declarations"] = [ast_to_dict(d) for d in node.declarations]
    
    if hasattr(node, 'params') and node.params:
        result["params"] = [ast_to_dict(p) for p in node.params]
    
    if hasattr(node, 'fields') and node.fields:
        result["fields"] = [ast_to_dict(f) for f in node.fields]
    
    if hasattr(node, 'body'):
        result["body"] = ast_to_dict(node.body)
    
    if hasattr(node, 'statements') and node.statements:
        result["statements"] = [ast_to_dict(s) for s in node.statements]
    
    if hasattr(node, 'condition'):
        result["condition"] = ast_to_dict(node.condition)
    
    if hasattr(node, 'then_branch'):
        result["then_branch"] = ast_to_dict(node.then_branch)
    
    if hasattr(node, 'else_branch'):
        result["else_branch"] = ast_to_dict(node.else_branch)
    
    if hasattr(node, 'init'):
        result["init"] = ast_to_dict(node.init)
    
    if hasattr(node, 'update'):
        result["update"] = ast_to_dict(node.update)
    
    if hasattr(node, 'left'):
        result["left"] = ast_to_dict(node.left)
    
    if hasattr(node, 'right'):
        result["right"] = ast_to_dict(node.right)
    
    if hasattr(node, 'operand'):
        result["operand"] = ast_to_dict(node.operand)
    
    if hasattr(node, 'callee'):
        result["callee"] = node.callee.name if hasattr(node.callee, 'name') else str(node.callee)
    
    if hasattr(node, 'arguments') and node.arguments:
        result["arguments"] = [ast_to_dict(a) for a in node.arguments]
    
    if hasattr(node, 'target'):
        result["target"] = ast_to_dict(node.target)
    
    if hasattr(node, 'initializer'):
        result["initializer"] = ast_to_dict(node.initializer)
    
    return result


def main():
    """Главная функция - обрабатывает команды"""
    if len(sys.argv) < 2:
        print_usage()
        return 1

    command = sys.argv[1]

    if command == "--help" or command == "-h":
        print_usage()
        return 0

    elif command == "test":
        return run_tests("lexer")

    elif command == "test-parser":
        return run_tests("parser")

    elif command == "test-semantic":
        return run_tests("semantic")

    elif command == "lex":
        if len(sys.argv) < 3:
            print("Ошибка: укажите файл для анализа")
            return 1
        return run_lexer(sys.argv[2])

    elif command == "parse":
        return run_parser(sys.argv[2:])

    elif command == "check" or command == "semantic":
        return run_semantic_analysis(sys.argv[2:])

    else:
        # Для обратной совместимости: если просто файл без команды
        filename = sys.argv[1]
        return run_lexer(filename)


if __name__ == "__main__":
    sys.exit(main())