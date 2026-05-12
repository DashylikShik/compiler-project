"""IR instruction definitions and data structures"""

from dataclasses import dataclass, field
from typing import List, Optional, Any
from enum import Enum
from semantic.type_system import Type, BaseType


class InstructionType(Enum):
    """Types of IR instructions"""
    # Arithmetic
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    NEG = "neg"
    
    # Logical
    AND = "and"
    OR = "or"
    NOT = "not"
    XOR = "xor"
    
    # Comparisons
    CMP_EQ = "cmp_eq"
    CMP_NE = "cmp_ne"
    CMP_LT = "cmp_lt"
    CMP_LE = "cmp_le"
    CMP_GT = "cmp_gt"
    CMP_GE = "cmp_ge"
    
    # Memory
    LOAD = "load"
    STORE = "store"
    ALLOCA = "alloca"
    
    # Control flow
    LABEL = "label"
    JUMP = "jump"
    JUMP_IF = "jump_if"
    JUMP_IF_NOT = "jump_if_not"
    PHI = "phi"
    
    # Functions
    CALL = "call"
    RETURN = "return"
    PARAM = "param"
    
    # Data movement
    MOVE = "move"
    
    # Special
    COMMENT = "comment"


@dataclass
class Operand:
    """IR operand (can be temporary, variable, constant, or label)"""
    value: Any
    operand_type: str = "temp"  # temp, var, const, label
    ir_type: Optional[Type] = None
    
    def __str__(self):
        if self.operand_type == "const":
            return str(self.value)
        elif self.operand_type == "label":
            return f"{self.value}"
        else:
            return f"{self.value}"
    
    @classmethod
    def temp(cls, name: str, ir_type: Type = None):
        return cls(name, "temp", ir_type)
    
    @classmethod
    def var(cls, name: str, ir_type: Type = None):
        return cls(name, "var", ir_type)
    
    @classmethod
    def const(cls, value: Any, ir_type: Type = None):
        return cls(value, "const", ir_type)
    
    @classmethod
    def label(cls, name: str):
        return cls(name, "label")


@dataclass
class Instruction:
    """Single IR instruction"""
    type: InstructionType
    dest: Optional[Operand] = None
    src1: Optional[Operand] = None
    src2: Optional[Operand] = None
    label: Optional[str] = None
    args: List[Operand] = field(default_factory=list)
    comment: Optional[str] = None
    
    def __str__(self):
        if self.type == InstructionType.LABEL:
            return f"{self.label}:"
        elif self.type == InstructionType.COMMENT:
            return f"  # {self.comment}"
        elif self.type in [InstructionType.JUMP, InstructionType.JUMP_IF, InstructionType.JUMP_IF_NOT]:
            if self.type == InstructionType.JUMP:
                return f"  jump {self.src1}"
            elif self.type == InstructionType.JUMP_IF:
                return f"  jump_if {self.src1}, {self.src2}"
            else:
                return f"  jump_if_not {self.src1}, {self.src2}"
        elif self.type == InstructionType.RETURN:
            return f"  return {self.src1}" if self.src1 else "  return"
        elif self.type == InstructionType.LOAD:
            return f"  {self.dest} = load {self.src1}"
        elif self.type == InstructionType.STORE:
            return f"  store {self.src1}, {self.src2}"
        elif self.type == InstructionType.ALLOCA:
            return f"  {self.dest} = alloca {self.src1}"
        elif self.type == InstructionType.CALL:
            args_str = ", ".join(str(a) for a in self.args)
            if self.dest:
                return f"  {self.dest} = call {self.src1}({args_str})"
            return f"  call {self.src1}({args_str})"
        elif self.type == InstructionType.PHI:
            args_str = ", ".join(str(a) for a in self.args)
            return f"  {self.dest} = phi({args_str})"
        elif self.type == InstructionType.MOVE:
            return f"  {self.dest} = {self.src1}"
        elif self.type == InstructionType.PARAM:
            return f"  param {self.src1}, {self.src2}"
        else:
            # Binary operations
            return f"  {self.dest} = {self.type.value} {self.src1}, {self.src2}"


@dataclass
class IRFunction:
    """IR representation of a function"""
    name: str
    return_type: Type
    parameters: List[tuple] = field(default_factory=list)
    basic_blocks: List['BasicBlock'] = field(default_factory=list)
    local_vars: dict = field(default_factory=dict)
    temp_counter: int = 0
    label_counter: int = 0
    
    def new_temp(self, ir_type: Type = None) -> Operand:
        """Create a new temporary variable"""
        self.temp_counter += 1
        return Operand.temp(f"t{self.temp_counter}", ir_type)
    
    def new_label(self) -> str:
        """Create a new label"""
        self.label_counter += 1
        return f"L{self.label_counter}"


@dataclass
class IRProgram:
    """Complete IR program"""
    functions: List[IRFunction] = field(default_factory=list)
    global_vars: dict = field(default_factory=dict)
    
    def add_function(self, func: IRFunction):
        self.functions.append(func)
    
    def get_function(self, name: str) -> Optional[IRFunction]:
        for func in self.functions:
            if func.name == name:
                return func
        return None