"""Symbol table for semantic analysis"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from .type_system import Type, BaseType


class SymbolKind(Enum):
    """Kind of symbol"""
    VARIABLE = "variable"
    PARAMETER = "parameter"
    FUNCTION = "function"
    STRUCT = "struct"
    FIELD = "field"


@dataclass
class SymbolInfo:
    """Information stored for each symbol"""
    name: str
    kind: SymbolKind
    type: Type
    line: int
    column: int
    # For functions
    parameters: Optional[List['SymbolInfo']] = None
    return_type: Optional[Type] = None
    # For variables
    initialized: bool = False
    stack_offset: int = -1
    # For structs
    fields: Optional[Dict[str, Type]] = None
    
    def __str__(self):
        base = f"{self.kind.value} '{self.name}' of type {self.type} at {self.line}:{self.column}"
        if self.kind == SymbolKind.FUNCTION:
            params = ", ".join([str(p.type) for p in (self.parameters or [])])
            return f"Function '{self.name}({params}) -> {self.return_type}'"
        return base


class Scope:
    """Represents a single scope in the symbol table"""
    
    def __init__(self, name: str = "global", level: int = 0):
        self.name = name
        self.level = level
        self.symbols: Dict[str, SymbolInfo] = {}
        self.parent: Optional['Scope'] = None
    
    def insert(self, symbol: SymbolInfo) -> bool:
        """Insert symbol into this scope, return False if duplicate"""
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True
    
    def lookup_local(self, name: str) -> Optional[SymbolInfo]:
        """Look up symbol only in this scope"""
        return self.symbols.get(name)
    
    def __str__(self):
        return f"Scope({self.name}, level={self.level}, symbols={list(self.symbols.keys())})"


class SymbolTable:
    """Hierarchical symbol table with scope nesting"""
    
    def __init__(self):
        self.global_scope = Scope("global", 0)
        self.current_scope = self.global_scope
        self.scope_stack: List[Scope] = [self.global_scope]
    
    def enter_scope(self, name: str = "block"):
        """Enter a new nested scope"""
        new_scope = Scope(name, self.current_scope.level + 1)
        new_scope.parent = self.current_scope
        self.current_scope = new_scope
        self.scope_stack.append(new_scope)
    
    def exit_scope(self) -> Scope:
        """Exit current scope and return to parent"""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
        return self.current_scope
    
    def insert(self, name: str, symbol_info: SymbolInfo) -> bool:
        """Insert symbol into current scope"""
        return self.current_scope.insert(symbol_info)
    
    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """Look up symbol from current scope outward"""
        scope = self.current_scope
        while scope:
            symbol = scope.lookup_local(name)
            if symbol:
                return symbol
            scope = scope.parent
        return None
    
    def lookup_local(self, name: str) -> Optional[SymbolInfo]:
        """Look up symbol only in current scope"""
        return self.current_scope.lookup_local(name)
    
    def lookup_global(self, name: str) -> Optional[SymbolInfo]:
        """Look up symbol only in global scope"""
        return self.global_scope.lookup_local(name)
    
    def get_current_scope_name(self) -> str:
        """Get name of current scope"""
        return self.current_scope.name
    
    def get_scope_level(self) -> int:
        """Get current scope nesting level"""
        return self.current_scope.level
    
    def get_all_symbols(self) -> Dict[str, List[SymbolInfo]]:
        """Get all symbols organized by scope"""
        result = {}
        
        def collect(scope: Scope, name: str):
            if scope.symbols:
                result[name] = list(scope.symbols.values())
            if scope.parent:
                collect(scope.parent, f"parent_of_{name}")
        
        collect(self.current_scope, "current")
        return result
    
    def dump(self) -> str:
        """Dump symbol table as string for debugging"""
        lines = []
        lines.append("SYMBOL TABLE DUMP")
        
        def dump_scope(scope: Scope, indent: int):
            if not scope:
                return
            lines.append("  " * indent + f"Scope: {scope.name} (level {scope.level})")
            for name, symbol in scope.symbols.items():
                lines.append("  " * (indent + 1) + str(symbol))
            if scope.parent:
                dump_scope(scope.parent, indent + 1)
        
        dump_scope(self.current_scope, 0)
        return "\n".join(lines)
    
    def __str__(self):
        return self.dump()