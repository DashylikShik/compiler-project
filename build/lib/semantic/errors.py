"""Semantic error handling"""

from typing import Optional


class SemanticError:
    """Represents a semantic error"""
    
    def __init__(self, message: str, line: int, column: int, 
                 file: str = "<input>", error_type: str = "semantic error"):
        self.message = message
        self.line = line
        self.column = column
        self.file = file
        self.error_type = error_type
    
    def __str__(self):
        return f"{self.error_type}: {self.message}\n  --> {self.file}:{self.line}:{self.column}"
    
    def format_with_context(self, source_lines: Optional[list] = None) -> str:
        """Format error with source code context"""
        result = [str(self)]
        
        if source_lines and 1 <= self.line <= len(source_lines):
            line_content = source_lines[self.line - 1].rstrip()
            result.append(f"   |")
            result.append(f"{self.line:3} | {line_content}")
            result.append(f"   | {' ' * (self.column - 1)}^")
        
        return "\n".join(result)


class DuplicateDeclarationError(SemanticError):
    def __init__(self, name: str, line: int, column: int, prev_line: int = None):
        msg = f"duplicate declaration of '{name}'"
        if prev_line:
            msg += f" (previously declared at line {prev_line})"
        super().__init__(msg, line, column, error_type="duplicate declaration")


class UndeclaredIdentifierError(SemanticError):
    def __init__(self, name: str, line: int, column: int, suggestion: str = None):
        msg = f"undeclared identifier '{name}'"
        if suggestion:
            msg += f"\n   = note: did you mean '{suggestion}'?"
        super().__init__(msg, line, column, error_type="undeclared identifier")


class TypeMismatchError(SemanticError):
    def __init__(self, line: int, column: int, expected: str, found: str, context: str = ""):
        msg = f"type mismatch{context}: expected {expected}, found {found}"
        super().__init__(msg, line, column, error_type="type mismatch")


class ArgumentCountError(SemanticError):
    def __init__(self, line: int, column: int, expected: int, found: int, func_name: str):
        msg = f"argument count mismatch in call to '{func_name}': expected {expected}, found {found}"
        super().__init__(msg, line, column, error_type="argument count mismatch")


class InvalidReturnTypeError(SemanticError):
    def __init__(self, line: int, column: int, expected: str, found: str):
        msg = f"invalid return type: expected {expected}, found {found}"
        super().__init__(msg, line, column, error_type="invalid return type")


class InvalidConditionError(SemanticError):
    def __init__(self, line: int, column: int, found: str):
        msg = f"invalid condition type: expected bool, found {found}"
        super().__init__(msg, line, column, error_type="invalid condition")


class InvalidAssignmentTargetError(SemanticError):
    def __init__(self, line: int, column: int):
        msg = "invalid assignment target (left-hand side must be a variable)"
        super().__init__(msg, line, column, error_type="invalid assignment")