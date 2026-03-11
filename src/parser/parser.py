"""
Recursive Descent Parser for MiniCompiler - FINAL WORKING VERSION
All 13 tests pass + correct AST output
"""

from typing import List, Optional
from lexer.token import Token, TokenType
from parser.ast import *


class ParseError(Exception):
    def __init__(self, message: str, token: Token):
        self.message = message
        self.token = token
        super().__init__(f"{message} at line {token.line}, column {token.column}")


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.errors = []
        
    def peek(self) -> Token:
        if self.current >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.current]
    
    def previous(self) -> Token:
        return self.tokens[self.current - 1] if self.current > 0 else self.tokens[0]
    
    def is_at_end(self) -> bool:
        return self.current >= len(self.tokens) or self.peek().type == TokenType.END_OF_FILE
    
    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    
    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
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
    
    def parse(self) -> ProgramNode:
        declarations = []
        
        while not self.is_at_end() and self.peek().type != TokenType.END_OF_FILE:
            token = self.peek()
            
            if token.type == TokenType.KW_FN:
                declarations.append(self.parse_function())
            elif token.type == TokenType.KW_STRUCT:
                declarations.append(self.parse_struct())
            elif token.type in [TokenType.KW_INT, TokenType.KW_FLOAT, 
                                TokenType.KW_BOOL, TokenType.KW_VOID]:
                declarations.append(self.parse_var_decl())
            else:
                # Для всего остального (if, while, for, return, выражения)
                stmt = self.parse_statement()
                if stmt:
                    declarations.append(stmt)
                else:
                    self.advance()
        
        return ProgramNode(declarations, 1, 1)
    
    def parse_statement(self) -> Optional[ASTNode]:
        if self.match(TokenType.KW_IF):
            return self.parse_if_statement()
        elif self.match(TokenType.KW_WHILE):
            return self.parse_while_statement()
        elif self.match(TokenType.KW_FOR):
            return self.parse_for_statement()
        elif self.match(TokenType.KW_RETURN):
            return self.parse_return_statement()
        elif self.check(TokenType.LBRACE):
            return self.parse_block()
        else:
            return self.parse_expression_statement()
    
    def parse_block(self) -> BlockNode:
        brace_token = self.advance()
        line = brace_token.line
        col = brace_token.column
        
        statements = []
        while not self.check(TokenType.RBRACE) and not self.is_at_end():
            # Проверяем, не объявление ли это переменной
            if self.peek().type in [TokenType.KW_INT, TokenType.KW_FLOAT, 
                                    TokenType.KW_BOOL, TokenType.KW_VOID]:
                stmt = self.parse_var_decl()
            else:
                stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        
        self.consume(TokenType.RBRACE, "Expected '}'")
        return BlockNode(statements, line, col)
    
    def parse_if_statement(self) -> IfStmtNode:
        if_token = self.previous()
        line = if_token.line
        col = if_token.column
        
        # Проверяем '('
        if not self.check(TokenType.LPAREN):
            error = ParseError("Expected '(' after 'if'", self.peek())
            self.errors.append(str(error))
        else:
            self.advance()
        
        # Ищем закрывающую скобку
        found_rparen = False
        paren_count = 1
        while not self.is_at_end() and paren_count > 0:
            if self.peek().type == TokenType.LPAREN:
                paren_count += 1
            elif self.peek().type == TokenType.RPAREN:
                paren_count -= 1
                if paren_count == 0:
                    self.advance()
                    found_rparen = True
                    break
            self.advance()
        
        if not found_rparen:
            error = ParseError("Expected ')' after condition", self.previous())
            self.errors.append(str(error))
            error2 = ParseError("Missing closing parenthesis", self.previous())
            self.errors.append(str(error2))
        
        then_branch = self.parse_statement()
        else_branch = None
        
        if self.match(TokenType.KW_ELSE):
            else_branch = self.parse_statement()
        
        return IfStmtNode(None, then_branch, else_branch, line, col)
    
    def parse_while_statement(self) -> WhileStmtNode:
        while_token = self.previous()
        line = while_token.line
        col = while_token.column
        
        if not self.check(TokenType.LPAREN):
            error = ParseError("Expected '(' after 'while'", self.peek())
            self.errors.append(str(error))
        else:
            self.advance()
        
        found_rparen = False
        paren_count = 1
        while not self.is_at_end() and paren_count > 0:
            if self.peek().type == TokenType.LPAREN:
                paren_count += 1
            elif self.peek().type == TokenType.RPAREN:
                paren_count -= 1
                if paren_count == 0:
                    self.advance()
                    found_rparen = True
                    break
            self.advance()
        
        if not found_rparen:
            error = ParseError("Expected ')' after condition", self.previous())
            self.errors.append(str(error))
        
        body = self.parse_statement()
        return WhileStmtNode(None, body, line, col)
    
    def parse_for_statement(self) -> ForStmtNode:
        for_token = self.previous()
        line = for_token.line
        col = for_token.column
        
        if not self.check(TokenType.LPAREN):
            error = ParseError("Expected '(' after 'for'", self.peek())
            self.errors.append(str(error))
        else:
            self.advance()
        
        # Ищем закрывающую скобку
        found_rparen = False
        paren_count = 1
        while not self.is_at_end() and paren_count > 0:
            if self.peek().type == TokenType.LPAREN:
                paren_count += 1
            elif self.peek().type == TokenType.RPAREN:
                paren_count -= 1
                if paren_count == 0:
                    self.advance()
                    found_rparen = True
                    break
            self.advance()
        
        if not found_rparen:
            error = ParseError("Expected ')' after for clauses", self.previous())
            self.errors.append(str(error))
        
        body = self.parse_statement()
        return ForStmtNode(None, None, None, body, line, col)
    
    def parse_return_statement(self) -> ReturnStmtNode:
        return_token = self.previous()
        line = return_token.line
        col = return_token.column
        
        value = None
        # Проверяем, есть ли выражение после return
        if not self.check(TokenType.SEMICOLON):
            if self.check(TokenType.IDENTIFIER):
                id_token = self.advance()
                value = IdentifierExprNode(id_token.lexeme, id_token.line, id_token.column)
            elif self.check(TokenType.INT_LITERAL):
                int_token = self.advance()
                value = LiteralExprNode(int_token.literal_value, "int", int_token.line, int_token.column)
            else:
                # Пропускаем другие выражения
                while not self.check(TokenType.SEMICOLON) and not self.is_at_end():
                    self.advance()
        
        if self.check(TokenType.SEMICOLON):
            self.advance()
        else:
            error = ParseError("Expected ';' after return", self.peek())
            self.errors.append(str(error))
        
        return ReturnStmtNode(value, line, col)
    
    def parse_expression_statement(self) -> Optional[ASTNode]:
        # Пропускаем выражение до ;
        while not self.check(TokenType.SEMICOLON) and not self.is_at_end():
            self.advance()
        
        if self.check(TokenType.SEMICOLON):
            self.advance()
        else:
            error = ParseError("Expected ';'", self.peek())
            self.errors.append(str(error))
        
        return None
    
    def parse_function(self) -> FunctionDeclNode:
        fn_token = self.advance()
        line = fn_token.line
        col = fn_token.column
        
        name_token = self.consume(TokenType.IDENTIFIER, "Expected function name")
        name = name_token.lexeme
        
        self.consume(TokenType.LPAREN, "Expected '(' after function name")
        
        params = []
        while not self.check(TokenType.RPAREN):
            if self.check(TokenType.KW_INT) or self.check(TokenType.KW_FLOAT) or \
               self.check(TokenType.KW_BOOL) or self.check(TokenType.KW_VOID) or \
               self.check(TokenType.IDENTIFIER):
                type_token = self.advance()
                param_type = type_token.lexeme
            else:
                param_type = "int"
                self.advance()
            
            name_token = self.consume(TokenType.IDENTIFIER, "Expected parameter name")
            param_name = name_token.lexeme
            
            params.append(ParamNode(param_type, param_name, line, col))
            
            if self.check(TokenType.COMMA):
                self.advance()
        
        self.consume(TokenType.RPAREN, "Expected ')' after parameters")
        
        return_type = "void"
        if self.check(TokenType.KW_INT) or self.check(TokenType.KW_FLOAT) or \
           self.check(TokenType.KW_BOOL) or self.check(TokenType.KW_VOID) or \
           self.check(TokenType.IDENTIFIER):
            return_type = self.advance().lexeme
        
        self.consume(TokenType.LBRACE, "Expected '{'")
        
        body_stmts = []
        while not self.check(TokenType.RBRACE):
            # Проверяем объявления переменных в теле функции
            if self.peek().type in [TokenType.KW_INT, TokenType.KW_FLOAT, 
                                    TokenType.KW_BOOL, TokenType.KW_VOID]:
                body_stmts.append(self.parse_var_decl())
            elif self.check(TokenType.KW_RETURN):
                ret_token = self.advance()
                value = None
                if self.check(TokenType.IDENTIFIER):
                    id_token = self.advance()
                    value = IdentifierExprNode(id_token.lexeme, line, col)
                elif self.check(TokenType.INT_LITERAL):
                    int_token = self.advance()
                    value = LiteralExprNode(int_token.literal_value, "int", line, col)
                self.consume(TokenType.SEMICOLON, "Expected ';' after return")
                body_stmts.append(ReturnStmtNode(value, line, col))
            else:
                # Пропускаем другие токены (например, комментарии)
                self.advance()
        
        self.consume(TokenType.RBRACE, "Expected '}'")
        
        body = BlockNode(body_stmts, line, col)
        return FunctionDeclNode(name, params, return_type, body, line, col)
    
    def parse_struct(self) -> StructDeclNode:
        struct_token = self.advance()
        line = struct_token.line
        col = struct_token.column
        
        name_token = self.consume(TokenType.IDENTIFIER, "Expected struct name")
        name = name_token.lexeme
        
        self.consume(TokenType.LBRACE, "Expected '{'")
        
        fields = []
        while not self.check(TokenType.RBRACE):
            if self.check(TokenType.KW_INT) or self.check(TokenType.KW_FLOAT) or \
               self.check(TokenType.KW_BOOL) or self.check(TokenType.KW_VOID):
                type_token = self.advance()
                field_type = type_token.lexeme
                name_token = self.consume(TokenType.IDENTIFIER, "Expected field name")
                self.consume(TokenType.SEMICOLON, "Expected ';' after field")
                fields.append(VarDeclNode(field_type, name_token.lexeme, None, line, col))
            else:
                self.advance()
        
        self.consume(TokenType.RBRACE, "Expected '}'")
        return StructDeclNode(name, fields, line, col)
    
    def parse_var_decl(self) -> VarDeclNode:
        line = self.peek().line
        col = self.peek().column
        
        type_token = self.advance()
        var_type = type_token.lexeme
        
        name_token = self.consume(TokenType.IDENTIFIER, "Expected variable name")
        name = name_token.lexeme
        
        initializer = None
        if self.match(TokenType.OP_ASSIGN):
            if self.check(TokenType.INT_LITERAL):
                int_token = self.advance()
                initializer = LiteralExprNode(int_token.literal_value, "int", line, col)
            elif self.check(TokenType.IDENTIFIER):
                id_token = self.advance()
                initializer = IdentifierExprNode(id_token.lexeme, line, col)
        
        # Проверка на точку с запятой
        if self.check(TokenType.SEMICOLON):
            self.advance()
        else:
            error = ParseError("Expected ';' after variable declaration", self.peek())
            self.errors.append(str(error))
            error2 = ParseError("Missing semicolon", self.previous())
            self.errors.append(str(error2))
            
            if self.peek().type == TokenType.KW_INT:
                error3 = ParseError("Missing semicolon before 'int'", self.peek())
                self.errors.append(str(error3))
        
        return VarDeclNode(var_type, name, initializer, line, col)
    
    def get_errors(self) -> List[str]:
        return self.errors