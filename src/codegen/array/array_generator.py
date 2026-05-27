"""Array code generation for Sprint 7"""

from typing import List, Optional
from ...ir.ir_instructions import Operand


class ArrayGenerator:
    """Generates assembly for array operations"""
    
    def __init__(self, sections, stack_frame, temp_offset):
        self.sections = sections
        self.stack_frame = stack_frame
        self.temp_offset = temp_offset
        self.array_offsets = {}
    
    def allocate_array(self, name: str, size: int, element_size: int = 4) -> int:
        """Allocate array on stack"""
        total_size = size * element_size
        total_size = (total_size + 15) & ~15  # Align to 16 bytes
        
        if self.stack_frame:
            offset = self.stack_frame.allocate_local(name, total_size)
            self.array_offsets[name] = offset.offset
            return offset.offset
        return 0
    
    def get_element_address(self, base: str, index: str, element_size: int) -> str:
        """Calculate address of array element"""
        return f"{base} + {index} * {element_size}"
    
    def generate_array_access(self, base: str, index: str, element_size: int, dest: str):
        """Generate assembly for array element access"""
        self.sections['text'].append(f"    mov rax, {base}")
        self.sections['text'].append(f"    mov rbx, {index}")
        self.sections['text'].append(f"    imul rbx, {element_size}")
        self.sections['text'].append(f"    add rax, rbx")
        self.sections['text'].append(f"    mov {dest}, [rax]")
    
    def generate_array_store(self, base: str, index: str, value: str, element_size: int):
        """Generate assembly for array element store"""
        self.sections['text'].append(f"    mov rax, {base}")
        self.sections['text'].append(f"    mov rbx, {index}")
        self.sections['text'].append(f"    imul rbx, {element_size}")
        self.sections['text'].append(f"    add rax, rbx")
        self.sections['text'].append(f"    mov [rax], {value}")