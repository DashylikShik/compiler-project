import sys
import pytest
import os
import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from typing import List, Optional
from lexer.token import Token, TokenType
from parser.ast import *
from utils.ast_printer import ASTPrinter
from utils.ast_dot import ASTDotGenerator

class ParseError(Exception):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"[Line {token.line}, Col {token.column}] {message}. Got: {token.type} ('{token.lexeme}')")

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors = []
        
    # HELPER METHODS
    
    def peek(self) -> Token:
        if self.current >= len(self.tokens):
            return self.tokens[-1]     # Возвращает токен, на котором мы стоим, НЕ съедая его.
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1] if self.current > 0 else self.tokens[0]
    
    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.END_OF_FILE
    
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():     # Использует peek(), чтобы спросить: "Следующее слово точно такое-то?"
            return False
        return self.peek().type == token_type
    
    def match(self, *types: TokenType) -> bool:
        for token_type in types:
            if self.check(token_type):
                self.advance()
                return True
        return False
    
    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        error = ParseError(message, self.peek())
        self.errors.append(str(error))
        return self.peek()

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON: return
            if self.peek().type in [TokenType.KW_FN, TokenType.KW_STRUCT, 
                                    TokenType.KW_IF, TokenType.KW_WHILE, 
                                    TokenType.KW_FOR, TokenType.KW_RETURN]:
                return
            self.advance()
    
    
    def parse(self) -> ProgramNode:
        declarations = []
        
        while not self.is_at_end():
            try:
                decl = self.declaration()
                if decl:
                    declarations.append(decl)
            except ParseError as e:
                self.errors.append(str(e))
                self.synchronize()
        
        return ProgramNode(declarations, 1, 1)

    def declaration(self):
        if self.match(TokenType.KW_FN):
            return self.function_declaration()
        if self.match(TokenType.KW_STRUCT):
            return self.struct_declaration()
        
        if self.check_type_start():
            return self.var_declaration()
            
        return self.statement()

    def check_type_start(self):
        if self.check(TokenType.KW_INT) or self.check(TokenType.KW_FLOAT) or \
           self.check(TokenType.KW_BOOL) or self.check(TokenType.KW_VOID):
            return True
        if self.check(TokenType.IDENTIFIER):
            # Lookahead
            if self.current + 1 < len(self.tokens) and self.tokens[self.current+1].type == TokenType.IDENTIFIER:
                return True
        return False

    def type_spec(self) -> str:
        if self.match(TokenType.KW_INT): return "int"
        if self.match(TokenType.KW_FLOAT): return "float"
        if self.match(TokenType.KW_BOOL): return "bool"
        if self.match(TokenType.KW_VOID): return "void"
        if self.match(TokenType.IDENTIFIER): return self.previous().lexeme
        
        raise ParseError("Expect type specifier", self.peek())


    def function_declaration(self) -> FunctionDeclNode:
        fn_token = self.previous()
        name_tok = self.consume(TokenType.IDENTIFIER, "Expect function name")
        name = name_tok.lexeme
        
        self.consume(TokenType.LPAREN, "Expect '(' after function name")
        params = []
        if not self.check(TokenType.RPAREN):
            params = self.parameters()
        self.consume(TokenType.RPAREN, "Expect ')' after parameters")

        return_type = "void"
        if self.match(TokenType.OP_ARROW): 
             return_type = self.type_spec()
        
        body = self.block()
        
        return FunctionDeclNode(name, return_type, params, body, fn_token.line, fn_token.column)

    def struct_declaration(self) -> StructDeclNode:
        struct_token = self.previous()
        name_tok = self.consume(TokenType.IDENTIFIER, "Expect struct name")
        self.consume(TokenType.LBRACE, "Expect '{' before struct body")
        
        fields = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            fields.append(self.var_declaration())
            
        self.consume(TokenType.RBRACE, "Expect '}' after struct body")
        return StructDeclNode(name_tok.lexeme, fields, struct_token.line, struct_token.column)

    def var_declaration(self) -> VarDeclStmtNode:
        type_name = self.type_spec()
        name_tok = self.consume(TokenType.IDENTIFIER, "Expect variable name")
        
        initializer = None
        if self.match(TokenType.OP_ASSIGN):
            initializer = self.expression()
            
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration")
        return VarDeclStmtNode(type_name, name_tok.lexeme, initializer, name_tok.line, name_tok.column)

    def parameters(self) -> List[ParamNode]:
        params = []
        params.append(self.parameter())
        while self.match(TokenType.COMMA):
            params.append(self.parameter())
        return params

    def parameter(self) -> ParamNode:
        type_name = self.type_spec()
        name_tok = self.consume(TokenType.IDENTIFIER, "Expect parameter name")
        return ParamNode(type_name, name_tok.lexeme, name_tok.line, name_tok.column)

    def statement(self) -> StatementNode:
        if self.match(TokenType.LBRACE): return self.block()
        if self.match(TokenType.KW_IF): return self.if_statement()
        if self.match(TokenType.KW_WHILE): return self.while_statement()
        if self.match(TokenType.KW_FOR): return self.for_statement()
        if self.match(TokenType.KW_RETURN): return self.return_statement()
        if self.match(TokenType.SEMICOLON): return None # Empty statement

        return self.expression_statement()

    def block(self) -> BlockStmtNode:

        if self.previous().type != TokenType.LBRACE:
             self.consume(TokenType.LBRACE, "Expect '{'")
        
        stmts = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            decl = self.declaration()
            if decl: stmts.append(decl)
        
        self.consume(TokenType.RBRACE, "Expect '}' after block")
        return BlockStmtNode(stmts, self.previous().line, self.previous().column)

    def if_statement(self) -> IfStmtNode:
        if_token = self.previous() # 'if'
        self.consume(TokenType.LPAREN, "Expect '(' after 'if'")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Expect ')' after if condition")
        
        then_branch = self.statement()
        else_branch = None
        
        if self.match(TokenType.KW_ELSE):
            else_branch = self.statement()
            
        return IfStmtNode(condition, then_branch, else_branch, if_token.line, if_token.column)

    def while_statement(self) -> WhileStmtNode:
        while_token = self.previous()
        self.consume(TokenType.LPAREN, "Expect '(' after 'while'")
        condition = self.expression()
        self.consume(TokenType.RPAREN, "Expect ')' after while condition")
        body = self.statement()
        return WhileStmtNode(condition, body, while_token.line, while_token.column)

    def for_statement(self) -> ForStmtNode:
        for_token = self.previous()
        self.consume(TokenType.LPAREN, "Expect '(' after 'for'")
        
        initializer = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.check_type_start():
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition")

        update = None
        if not self.check(TokenType.RPAREN):
            update = self.expression()
        self.consume(TokenType.RPAREN, "Expect ')' after for clauses")

        body = self.statement()
        return ForStmtNode(initializer, condition, update, body, for_token.line, for_token.column)

    def return_statement(self) -> ReturnStmtNode:
        ret_token = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value")
        return ReturnStmtNode(value, ret_token.line, ret_token.column)

    def expression_statement(self) -> ExprStmtNode:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression")
        return ExprStmtNode(expr, expr.line, expr.column)


    def expression(self) -> ExpressionNode:
        return self.assignment()

    def assignment(self) -> ExpressionNode:
        expr = self.logical_or()
        
        if self.match(TokenType.OP_ASSIGN, TokenType.OP_PLUS_ASSIGN, TokenType.OP_MINUS_ASSIGN, 
                      TokenType.OP_MULT_ASSIGN, TokenType.OP_DIV_ASSIGN):
            operator = self.previous()
            value = self.assignment() 
            
            if isinstance(expr, IdentifierExprNode):
                return AssignmentExprNode(expr, operator, value, expr.line, expr.column)
            else:
                self.errors.append(str(ParseError("Invalid assignment target", operator)))
                return expr
        
        return expr

    def logical_or(self) -> ExpressionNode:
        expr = self.logical_and()
        while self.match(TokenType.OP_OR_OR):
            operator = self.previous() 
            right = self.logical_and()
            expr = BinaryExprNode(expr, operator, right, expr.line, expr.column)
        return expr

    def logical_and(self) -> ExpressionNode:
        expr = self.equality()
        while self.match(TokenType.OP_AND_AND):
            operator = self.previous()  
            right = self.equality()
            expr = BinaryExprNode(expr, operator, right, expr.line, expr.column)
        return expr

    def equality(self) -> ExpressionNode:
        expr = self.relational()
        while self.match(TokenType.OP_EQ, TokenType.OP_NEQ):
            operator = self.previous() 
            right = self.relational()
            expr = BinaryExprNode(expr, operator, right, expr.line, expr.column)
        return expr

    def relational(self) -> ExpressionNode:
        expr = self.additive()
        while self.match(TokenType.OP_LT, TokenType.OP_LTE, TokenType.OP_GT, TokenType.OP_GTE):
            operator = self.previous() 
            right = self.additive()
            expr = BinaryExprNode(expr, operator, right, expr.line, expr.column)
        return expr

    def additive(self) -> ExpressionNode:
        expr = self.multiplicative()
        while self.match(TokenType.OP_PLUS, TokenType.OP_MINUS):
            operator = self.previous() 
            right = self.multiplicative()
            expr = BinaryExprNode(expr, operator, right, expr.line, expr.column)
        return expr

    def multiplicative(self) -> ExpressionNode:
        expr = self.unary()
        while self.match(TokenType.OP_MULT, TokenType.OP_DIV, TokenType.OP_MOD):
            operator = self.previous()
            right = self.unary()
            expr = BinaryExprNode(expr, operator, right, expr.line, expr.column)
        return expr

    def unary(self) -> ExpressionNode:
        if self.match(TokenType.OP_MINUS, TokenType.OP_NOT):
            operator = self.previous()
            right = self.unary()
            return UnaryExprNode(operator, right, operator.line, operator.column)
        return self.primary()

    def primary(self) -> ExpressionNode:
        if self.match(TokenType.INT_LITERAL):
            return LiteralExprNode(self.previous().literal_value, "int", self.previous().line, self.previous().column)
        if self.match(TokenType.FLOAT_LITERAL):
            return LiteralExprNode(self.previous().literal_value, "float", self.previous().line, self.previous().column)
        if self.match(TokenType.STRING_LITERAL):
            return LiteralExprNode(self.previous().literal_value, "string", self.previous().line, self.previous().column)
        if self.match(TokenType.KW_TRUE):
            return LiteralExprNode(True, "bool", self.previous().line, self.previous().column)
        if self.match(TokenType.KW_FALSE):
            return LiteralExprNode(False, "bool", self.previous().line, self.previous().column)
        
        if self.match(TokenType.IDENTIFIER):
            if self.match(TokenType.LPAREN):
                return self.finish_call()
            return IdentifierExprNode(self.previous().lexeme, self.previous().line, self.previous().column)
            
        if self.match(TokenType.LPAREN):
            expr = self.expression()
            self.consume(TokenType.RPAREN, "Expect ')' after expression")
            return expr

        raise ParseError("Expect expression", self.peek())

    def finish_call(self) -> CallExprNode:
        callee_id = self.tokens[self.current - 2]
        callee_node = IdentifierExprNode(callee_id.lexeme, callee_id.line, callee_id.column)
        
        arguments = []
        if not self.check(TokenType.RPAREN):
            arguments.append(self.expression())
            while self.match(TokenType.COMMA):
                arguments.append(self.expression())
        
        self.consume(TokenType.RPAREN, "Expect ')' after arguments")
        return CallExprNode(callee_node, arguments, callee_id.line, callee_id.column)

    def get_errors(self) -> List[str]:
        return self.errors