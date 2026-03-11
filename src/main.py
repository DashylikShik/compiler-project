#!/usr/bin/env python3
"""
Точка входа для компилятора
Поддерживает:
  Sprint 1: лексический анализ
  Sprint 2: синтаксический анализ + AST
"""

import sys
import os
import json

# Добавляем путь к пакетам
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from lexer.scanner import Scanner
from parser.parser import Parser
from utils.ast_printer import ASTPrinter
from utils.ast_dot import ASTDotGenerator


def print_usage():
    """Печатает информацию об использовании"""
    print("Использование:")
    print("  compiler lex <file.src>              # Только лексический анализ (Sprint 1)")
    print("  compiler parse <file.src>             # Синтаксический анализ + AST (Sprint 2)")
    print("  compiler parse --format [text|dot|json] <file.src>  # AST в разных форматах")
    print("  compiler parse --output <file> <file.src>           # Сохранить AST в файл")
    print("  compiler test                          # Запустить тесты лексера (Sprint 1)")
    print("  compiler test-parser                   # Запустить тесты парсера (Sprint 2)")
    print("  compiler --help                         # Показать помощь")
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


def ast_to_dict(node):
    """Конвертирует AST в словарь для JSON"""
    if node is None:
        return None
    
    # Базовая информация о узле
    result = {
        "type": node.node_type.value if hasattr(node, 'node_type') else "Unknown",
        "line": node.line,
        "column": node.column
    }
    
    # Добавляем атрибуты в зависимости от типа узла
    if hasattr(node, 'name'):
        result["name"] = node.name
    if hasattr(node, 'value'):
        # Для LiteralExprNode нужно преобразовать значение
        if isinstance(node.value, (str, int, float, bool)):
            result["value"] = node.value
        else:
            result["value"] = str(node.value)
    if hasattr(node, 'operator'):
        result["operator"] = node.operator
    if hasattr(node, 'var_type'):
        result["var_type"] = node.var_type
    if hasattr(node, 'return_type'):
        result["return_type"] = node.return_type
    if hasattr(node, 'literal_type'):
        result["literal_type"] = node.literal_type
    
    # Обрабатываем детей (всегда вызываем ast_to_dict рекурсивно)
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
        result["callee"] = node.callee
    
    if hasattr(node, 'arguments') and node.arguments:
        result["arguments"] = [ast_to_dict(a) for a in node.arguments]
    
    if hasattr(node, 'target'):
        result["target"] = node.target
    
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
        # Запуск тестов лексера (Sprint 1)
        test_runner = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'tests', 'test_runner.py'
        )
        if os.path.exists(test_runner):
            os.system(f'python "{test_runner}"')
        else:
            print("Ошибка: test_runner.py не найден")
        return 0

    elif command == "test-parser":
        # Запуск тестов парсера (Sprint 2) - ТВОЙ ДОБАВЛЕННЫЙ КОД
        test_parser = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'tests', 'test_parser.py'
        )
        if os.path.exists(test_parser):
            os.system(f'python "{test_parser}"')
        else:
            print("Ошибка: test_parser.py не найден")
        return 0

    elif command == "lex":
        # Только лексический анализ
        if len(sys.argv) < 3:
            print("Ошибка: укажите файл для анализа")
            return 1
        return run_lexer(sys.argv[2])

    elif command == "parse":
        # Синтаксический анализ с AST
        return run_parser(sys.argv[2:])

    else:
        # Для обратной совместимости: если просто файл без команды
        # то запускаем лексер (как в Sprint 1)
        filename = sys.argv[1]
        return run_lexer(filename)


if __name__ == "__main__":
    sys.exit(main())