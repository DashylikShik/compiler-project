"""Type system for semantic analysis"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class BaseType(Enum):
    """Basic types supported by the language"""
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    STRING = "string"
    VOID = "void"
    STRUCT = "struct"
    ARRAY = "array"
    UNKNOWN = "unknown"
    ERROR = "error"


@dataclass
class Type:
    """Represents a type in the type system"""
    base: BaseType
    struct_name: Optional[str] = None
    fields: Optional[Dict[str, 'Type']] = None
    param_types: Optional[List['Type']] = None
    return_type: Optional['Type'] = None
    size: int = 0
    alignment: int = 0
    
    def __hash__(self):
        return hash((self.base, self.struct_name))
    
    def __eq__(self, other):
        if not isinstance(other, Type):
            return False
        if self.base != other.base:
            return False
        if self.base == BaseType.STRUCT:
            return self.struct_name == other.struct_name
        return True
    
    def __str__(self):
        if self.base == BaseType.STRUCT:
            return f"struct {self.struct_name}" if self.struct_name else "struct"
        elif self.base == BaseType.ARRAY:
            return f"array"
        return self.base.value
    
    def is_numeric(self) -> bool:
        return self.base in (BaseType.INT, BaseType.FLOAT)
    
    def is_arithmetic(self) -> bool:
        return self.base in (BaseType.INT, BaseType.FLOAT)
    
    def can_convert_to(self, target: 'Type') -> bool:
        if self == target:
            return True
        if self.base == BaseType.INT and target.base == BaseType.FLOAT:
            return True
        return False
    
    def get_size(self) -> int:
        if self.size > 0:
            return self.size
        if self.base == BaseType.INT:
            return 4
        elif self.base == BaseType.FLOAT:
            return 4
        elif self.base == BaseType.BOOL:
            return 1
        elif self.base == BaseType.STRING:
            return 8
        elif self.base == BaseType.STRUCT:
            if self.fields:
                total = 0
                for field_type in self.fields.values():
                    total += field_type.get_size()
                return total
            return 0
        return 0
    
    def get_alignment(self) -> int:
        if self.alignment > 0:
            return self.alignment
        if self.base == BaseType.INT:
            return 4
        elif self.base == BaseType.FLOAT:
            return 4
        elif self.base == BaseType.BOOL:
            return 1
        elif self.base == BaseType.STRING:
            return 8
        elif self.base == BaseType.STRUCT:
            if self.fields:
                max_align = 1
                for field_type in self.fields.values():
                    max_align = max(max_align, field_type.get_alignment())
                return max_align
            return 1
        return 1


# ArrayType определяется ПОСЛЕ Type (используем forward reference через строку)
@dataclass
class ArrayType:
    """Array type for static arrays"""
    element_type: 'Type'  # используем строку для forward reference
    size: int
    element_size: int = 4
    
    def get_total_size(self) -> int:
        return self.element_size * self.size
    
    def __str__(self):
        return f"{self.element_type}[{self.size}]"


class TypeSystem:
    """Type system manager with built-in types and operations"""
    
    def __init__(self):
        self.builtin_types = {
            'int': Type(BaseType.INT, size=4, alignment=4),
            'float': Type(BaseType.FLOAT, size=4, alignment=4),
            'bool': Type(BaseType.BOOL, size=1, alignment=1),
            'string': Type(BaseType.STRING, size=8, alignment=8),
            'void': Type(BaseType.VOID),
            'error': Type(BaseType.ERROR),
        }
        self.struct_types: Dict[str, Type] = {}
        self.array_types: Dict[str, ArrayType] = {}
    
    def get_builtin(self, name: str) -> Optional[Type]:
        return self.builtin_types.get(name)
    
    def get_type(self, name: str) -> Optional[Type]:
        if name in self.builtin_types:
            return self.builtin_types[name]
        if name in self.struct_types:
            return self.struct_types[name]
        return None
    
    def define_struct(self, name: str, fields: Dict[str, Type]) -> Type:
        struct_type = Type(BaseType.STRUCT, struct_name=name, fields=fields)
        self.struct_types[name] = struct_type
        return struct_type
    
    def define_array(self, element_type: Type, size: int) -> ArrayType:
        return ArrayType(element_type, size)
    
    def get_binary_operator_result_type(self, op: str, left: Type, right: Type) -> Type:
        if op in ('+', '-', '*', '/', '%'):
            if left.base == BaseType.INT and right.base == BaseType.INT:
                return self.builtin_types['int']
            elif left.base == BaseType.FLOAT and right.base == BaseType.FLOAT:
                return self.builtin_types['float']
            elif left.base == BaseType.INT and right.base == BaseType.FLOAT:
                return self.builtin_types['float']
            elif left.base == BaseType.FLOAT and right.base == BaseType.INT:
                return self.builtin_types['float']
        elif op in ('==', '!=', '<', '<=', '>', '>='):
            if left.is_arithmetic() and right.is_arithmetic():
                return self.builtin_types['bool']
            elif left.base == BaseType.BOOL and right.base == BaseType.BOOL:
                return self.builtin_types['bool']
        elif op in ('&&', '||'):
            if left.base == BaseType.BOOL and right.base == BaseType.BOOL:
                return self.builtin_types['bool']
        elif op in ('=', '+=', '-=', '*=', '/='):
            return left
        
        return self.builtin_types['error']
    
    def get_unary_operator_result_type(self, op: str, operand: Type) -> Type:
        if op == '-':
            if operand.base in (BaseType.INT, BaseType.FLOAT):
                return operand
        elif op == '!':
            if operand.base == BaseType.BOOL:
                return self.builtin_types['bool']
        return self.builtin_types['error']
    
    def is_compatible(self, source: Type, target: Type) -> bool:
        if source.base == BaseType.ERROR or target.base == BaseType.ERROR:
            return True
        return source.can_convert_to(target) or source == target