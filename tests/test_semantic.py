#!/usr/bin/env python3
"""Unit tests for semantic analysis"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from lexer.scanner import Scanner
from parser.parser import Parser
from semantic.analyzer import SemanticAnalyzer
from semantic.symbol_table import SymbolTable, SymbolInfo, SymbolKind
from semantic.type_system import TypeSystem, Type, BaseType
from semantic.errors import *


class TestTypeSystem(unittest.TestCase):
    """Tests for type system"""
    
    def setUp(self):
        self.ts = TypeSystem()
    
    def test_builtin_types(self):
        self.assertIsNotNone(self.ts.get_builtin('int'))
        self.assertIsNotNone(self.ts.get_builtin('float'))
        self.assertIsNotNone(self.ts.get_builtin('bool'))
        self.assertIsNotNone(self.ts.get_builtin('string'))
        self.assertIsNotNone(self.ts.get_builtin('void'))
    
    def test_type_compatibility(self):
        int_type = self.ts.get_builtin('int')
        float_type = self.ts.get_builtin('float')
        bool_type = self.ts.get_builtin('bool')
        
        self.assertTrue(self.ts.is_compatible(int_type, int_type))
        self.assertTrue(self.ts.is_compatible(int_type, float_type))  # int -> float widening
        self.assertFalse(self.ts.is_compatible(float_type, int_type))  # No narrowing
        self.assertTrue(self.ts.is_compatible(bool_type, bool_type))
        self.assertFalse(self.ts.is_compatible(int_type, bool_type))
    
    def test_binary_operator_types(self):
        int_type = self.ts.get_builtin('int')
        float_type = self.ts.get_builtin('float')
        bool_type = self.ts.get_builtin('bool')
        
        # Arithmetic
        result = self.ts.get_binary_operator_result_type('+', int_type, int_type)
        self.assertEqual(result.base, BaseType.INT)
        
        result = self.ts.get_binary_operator_result_type('+', int_type, float_type)
        self.assertEqual(result.base, BaseType.FLOAT)
        
        # Comparison
        result = self.ts.get_binary_operator_result_type('==', int_type, int_type)
        self.assertEqual(result.base, BaseType.BOOL)
        
        # Logical
        result = self.ts.get_binary_operator_result_type('&&', bool_type, bool_type)
        self.assertEqual(result.base, BaseType.BOOL)


class TestSymbolTable(unittest.TestCase):
    """Tests for symbol table"""
    
    def setUp(self):
        self.st = SymbolTable()
        self.ts = TypeSystem()
    
    def test_basic_operations(self):
        int_type = self.ts.get_builtin('int')
        symbol = SymbolInfo('x', SymbolKind.VARIABLE, int_type, 1, 1)
        
        self.assertTrue(self.st.insert('x', symbol))
        self.assertIsNotNone(self.st.lookup('x'))
        self.assertEqual(self.st.lookup('x'), symbol)
    
    def test_scope_nesting(self):
        int_type = self.ts.get_builtin('int')
        symbol_global = SymbolInfo('x', SymbolKind.VARIABLE, int_type, 1, 1)
        self.st.insert('x', symbol_global)
        
        self.st.enter_scope('inner')
        symbol_inner = SymbolInfo('y', SymbolKind.VARIABLE, int_type, 2, 1)
        self.st.insert('y', symbol_inner)
        
        self.assertIsNotNone(self.st.lookup('x'))  # From outer scope
        self.assertIsNotNone(self.st.lookup('y'))  # From current scope
        
        self.st.exit_scope()
        self.assertIsNone(self.st.lookup('y'))  # No longer accessible
    
    def test_duplicate_prevention(self):
        int_type = self.ts.get_builtin('int')
        symbol1 = SymbolInfo('x', SymbolKind.VARIABLE, int_type, 1, 1)
        symbol2 = SymbolInfo('x', SymbolKind.VARIABLE, int_type, 2, 1)
        
        self.assertTrue(self.st.insert('x', symbol1))
        self.assertFalse(self.st.insert('x', symbol2))


class TestSemanticAnalyzerValid(unittest.TestCase):
    """Tests for semantic analyzer with valid programs"""
    
    def analyze_program(self, source):
        scanner = Scanner(source)
        if scanner.errors:
            return None, scanner.errors
        parser = Parser(scanner.tokens)
        ast = parser.parse()
        if parser.errors:
            return None, parser.errors
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast, source)
        return analyzer, analyzer.get_errors()
    
    def test_valid_declarations(self):
        source = """
        fn main() -> int {
            return 42;
        }
        """
        analyzer, errors = self.analyze_program(source)
        self.assertEqual(len(errors), 0)
    
    def test_valid_variable_declaration(self):
        source = """
        fn main() -> int {
            int x = 10;
            return x;
        }
        """
        analyzer, errors = self.analyze_program(source)
        self.assertEqual(len(errors), 0)
    
    def test_binary_operations(self):
        source = """
        fn main() -> int {
            int x = 5 + 3;
            int y = x * 2;
            return y;
        }
        """
        analyzer, errors = self.analyze_program(source)
        self.assertEqual(len(errors), 0)
    
    def test_function_call(self):
        source = """
        fn add(int a, int b) -> int {
            return a + b;
        }
        
        fn main() -> int {
            int result = add(5, 3);
            return result;
        }
        """
        analyzer, errors = self.analyze_program(source)
        self.assertEqual(len(errors), 0)


class TestSemanticAnalyzerInvalid(unittest.TestCase):
    """Tests for semantic analyzer with invalid programs"""
    
    def analyze_program(self, source):
        scanner = Scanner(source)
        if scanner.errors:
            return None, scanner.errors
        parser = Parser(scanner.tokens)
        ast = parser.parse()
        if parser.errors:
            return None, parser.errors
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast, source)
        return analyzer, analyzer.get_errors()
    
    def test_undeclared_variable(self):
        source = """
        fn main() -> int {
            x = 10;
            return x;
        }
        """
        analyzer, errors = self.analyze_program(source)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('undeclared' in str(e).lower() for e in errors))
    
    def test_type_mismatch(self):
        source = """
        fn main() -> int {
            int x = "hello";
            return x;
        }
        """
        analyzer, errors = self.analyze_program(source)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('type mismatch' in str(e).lower() for e in errors))
    
    def test_duplicate_function(self):
        source = """
        fn foo() -> int {
            return 1;
        }
        
        fn foo() -> int {
            return 2;
        }
        """
        analyzer, errors = self.analyze_program(source)
        self.assertGreater(len(errors), 0)
    
    def test_argument_count_mismatch(self):
        source = """
        fn bar(int a, int b) -> int {
            return a + b;
        }
        
        fn main() -> int {
            return bar(5);
        }
        """
        analyzer, errors = self.analyze_program(source)
        self.assertGreater(len(errors), 0)
        self.assertTrue(any('argument count' in str(e).lower() for e in errors))
    
    def test_invalid_condition(self):
        source = """
        fn main() -> int {
            int x = 5;
            if (x) {
                return 1;
            }
            return 0;
        }
        """
        analyzer, errors = self.analyze_program(source)
        self.assertGreater(len(errors), 0)
    
    def test_return_type_mismatch(self):
        source = """
        fn main() -> int {
            return true;
        }
        """
        analyzer, errors = self.analyze_program(source)
        self.assertGreater(len(errors), 0)
    
    def test_duplicate_struct(self):
        source = """
        struct Point {
            int x;
            int y;
        }
        
        struct Point {
            float x;
            float y;
        }
        """
        analyzer, errors = self.analyze_program(source)
        self.assertGreater(len(errors), 0)


def main():
    unittest.main()


if __name__ == '__main__':
    main()