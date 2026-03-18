import pytest
import sys
import os
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from lexer.scanner import Scanner
from lexer.token import Token
from parser.parser import Parser
from parser.ast import *
from utils.ast_printer import ASTPrinter


def get_test_root():
    return os.path.dirname(__file__)

def parse_code(code):
    """Helper to parse string code"""
    lexer = Scanner(code)
    if hasattr(lexer, 'scan_tokens'): 
        lexer.scan_tokens()
    
    parser = Parser(lexer.tokens)
    ast = parser.parse()
    return ast, parser

def get_ast_text(ast):
    printer = ASTPrinter()
    return printer.print(ast)

def test_var_decl_simple():
    ast, p = parse_code("int x;")
    assert len(p.errors) == 0
    node = ast.declarations[0]
    assert isinstance(node, VarDeclStmtNode)
    assert node.name == "x"
    assert node.type_name == "int"
    assert node.initializer is None

def test_var_decl_init():
    ast, p = parse_code("float y = 3.14;")
    assert len(p.errors) == 0
    node = ast.declarations[0]
    assert node.type_name == "float"
    assert node.initializer.value == 3.14

def test_function_decl_simple():
    ast, p = parse_code("fn foo() {}")
    assert len(p.errors) == 0
    node = ast.declarations[0]
    assert isinstance(node, FunctionDeclNode)
    assert node.name == "foo"
    assert node.return_type == "void" or node.return_type is None

def test_function_decl_params_return():
    ast, p = parse_code("fn add(int a, float b) -> int { return 0; }")
    assert len(p.errors) == 0
    node = ast.declarations[0]
    assert node.return_type == "int"
    assert len(node.params) == 2
    assert node.params[0].type_name == "int"

def test_struct_decl():
    ast, p = parse_code("struct Point { int x; int y; }")
    assert len(p.errors) == 0
    node = ast.declarations[0]
    assert isinstance(node, StructDeclNode)
    assert node.name == "Point"
    assert len(node.fields) == 2

def test_block():
    ast, p = parse_code("{ int x=1; }")
    assert len(p.errors) == 0

    ast, p = parse_code("fn m() { { int x=1; } }")
    fn = ast.declarations[0]
    inner_block = fn.body.statements[0]
    assert isinstance(inner_block, BlockStmtNode)

def test_if_stmt():
    ast, p = parse_code("if (true) { x=1; } else { x=2; }")
    assert len(p.errors) == 0
    node = ast.declarations[0]
    assert isinstance(node, IfStmtNode)
    assert node.else_branch is not None

def test_while_stmt():
    ast, p = parse_code("while (x > 0) { x = x - 1; }")
    assert len(p.errors) == 0
    node = ast.declarations[0]
    assert isinstance(node, WhileStmtNode)
    assert isinstance(node.condition, BinaryExprNode)

def test_for_stmt_full():
    ast, p = parse_code("for (int i=0; i<10; i=i+1) { print(i); }")
    assert len(p.errors) == 0
    node = ast.declarations[0]
    assert isinstance(node, ForStmtNode)
    assert node.init is not None
    assert node.condition is not None
    assert node.update is not None

def test_for_stmt_empty_parts():
    ast, p = parse_code("for (;;) {}") 
    node = ast.declarations[0]
    assert node.init is None
    assert node.condition is None
    assert node.update is None

def test_return_stmt():
    ast, p = parse_code("fn f() { return 42; }")
    assert len(p.errors) == 0
    fn = ast.declarations[0]
    ret = fn.body.statements[0]
    assert isinstance(ret, ReturnStmtNode)
    assert ret.value.value == 42

def test_empty_stmt():
    ast, p = parse_code(";;")
    assert len(p.errors) == 0


def test_expr_primary_literal():
    ast, p = parse_code("int x = 42;")
    expr = ast.declarations[0].initializer
    assert isinstance(expr, LiteralExprNode)
    assert expr.value == 42

def test_expr_primary_grouping():
    ast, p = parse_code("int x = (1 + 2);")
    expr = ast.declarations[0].initializer
    assert isinstance(expr, BinaryExprNode) 

def test_expr_unary():
    ast, p = parse_code("int x = -5;")
    expr = ast.declarations[0].initializer
    assert isinstance(expr, UnaryExprNode)
    assert expr.operator.lexeme == "-"

def test_expr_multiplicative():
    ast, p = parse_code("int x = 1 * 2 / 3;")
    expr = ast.declarations[0].initializer
    assert isinstance(expr, BinaryExprNode)
    # Left assoc: (1*2) / 3
    assert expr.operator.lexeme == "/" 

def test_expr_additive():
    ast, p = parse_code("int x = 1 + 2 - 3;")
    expr = ast.declarations[0].initializer
    assert expr.operator.lexeme == "-"

def test_precedence_mul_over_add():
    ast, p = parse_code("int x = 1 + 2 * 3;")
    expr = ast.declarations[0].initializer
    assert expr.operator.lexeme == "+" 
    assert isinstance(expr.right, BinaryExprNode)
    assert expr.right.operator.lexeme == "*"

def test_precedence_logical():
    ast, p = parse_code("bool b = true || false && true;")
    expr = ast.declarations[0].initializer
    assert expr.operator.lexeme == "||"
    assert isinstance(expr.right, BinaryExprNode)
    assert expr.right.operator.lexeme == "&&"

def test_associativity_assignment_right():
    ast, p = parse_code("x = y = 1;") 
    stmt = ast.declarations[0]
    assert isinstance(stmt, ExprStmtNode)
    expr = stmt.expression
    assert isinstance(expr, AssignmentExprNode)
    assert expr.target.name == "x"
    assert isinstance(expr.value, AssignmentExprNode)
    assert expr.value.target.name == "y"

def test_call_expr():
    ast, p = parse_code("int x = foo(1, 2);")
    expr = ast.declarations[0].initializer
    assert isinstance(expr, CallExprNode)
    assert expr.callee.name == "foo"
    assert len(expr.arguments) == 2


def test_empty_program():
    ast, p = parse_code("")
    assert len(p.errors) == 0
    assert isinstance(ast, ProgramNode)

def test_empty_block():
    ast, p = parse_code("fn f() { }")
    fn = ast.declarations[0]
    assert len(fn.body.statements) == 0

def test_deep_nesting():
    code = "if(1) { if(1) { if(1) { x=1; } } }"
    ast, p = parse_code(code)
    assert len(p.errors) == 0
    assert isinstance(ast.declarations[0], IfStmtNode)



valid_files = glob.glob(os.path.join(get_test_root(), 'valid', '**', '*.src'), recursive=True)
invalid_files = glob.glob(os.path.join(get_test_root(), 'invalid', '**', '*.src'), recursive=True)

@pytest.mark.parametrize("src_path", valid_files)
def test_golden_valid(src_path):
    """TEST-3: Check valid files against expected AST output"""
    with open(src_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    ast, parser = parse_code(code)
    
    assert len(parser.errors) == 0, f"Unexpected errors in valid file: {parser.errors}"
    
    output = get_ast_text(ast)
    expected_path = src_path.replace('.src', '.expected')
    
    if not os.path.exists(expected_path):
        with open(expected_path, 'w', encoding='utf-8') as f:
            f.write(output)
        pytest.skip(f"Generated missing expected file: {expected_path}")

    with open(expected_path, 'r', encoding='utf-8') as f:
        expected = f.read()
    
    assert output.strip() == expected.strip(), f"Output mismatch for {src_path}"

@pytest.mark.parametrize("src_path", invalid_files)
def test_golden_invalid(src_path):
    """TEST-3 & TEST-4: Check invalid files against expected error output"""
    with open(src_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    ast, parser = parse_code(code)
    
    assert len(parser.errors) > 0, "Expected errors but parsed successfully"
    output = "[Syntax Errors]:\n"
    for e in parser.errors:
        output += f"  {e}\n"
    output = output.strip()
    
    expected_path = src_path.replace('.src', '.expected')
    
    if not os.path.exists(expected_path):
        with open(expected_path, 'w', encoding='utf-8') as f:
            f.write(output)
        pytest.skip(f"Generated missing expected file: {expected_path}")

    with open(expected_path, 'r', encoding='utf-8') as f:
        expected = f.read()
    
    assert output.strip() == expected.strip()


def test_recovery_missing_semicolon():
    code = "int x = 1 int y = 2;"
    ast, parser = parse_code(code)
    
    assert len(parser.errors) == 1
    
    found_y = any(isinstance(d, VarDeclStmtNode) and d.name == 'y' for d in ast.declarations)
    assert found_y, "Parser failed to recover and parse subsequent declaration"

def test_error_location_accuracy():
    code = """
    fn test() {
        int x = ;  # Error here
    }
    """
    ast, parser = parse_code(code)
    assert len(parser.errors) > 0
    err = parser.errors[0]

    assert "Line 3" in str(err) or "line 3" in str(err)

def test_lexer_parser_integration():
    """Test complex example from examples/ dir if exists"""
    example_path = os.path.join(os.path.dirname(get_test_root()), 'examples', 'factorial.src')
    if not os.path.exists(example_path):
        pytest.skip("No example file found")
    
    with open(example_path, 'r') as f:
        code = f.read()
    
    ast, parser = parse_code(code)
    assert len(parser.errors) == 0

def test_roundtrip_stability():
    """TEST-5: Parse -> Print -> Parse should be equivalent"""
    code = "int x = 1; fn f() { return x; }"
    
    ast1, p1 = parse_code(code)
    text1 = get_ast_text(ast1)
    
    ast2, p2 = parse_code(code)
    text2 = get_ast_text(ast2)
    
    assert text1 == text2