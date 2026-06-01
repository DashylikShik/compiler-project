"""Stack frame management for x86-64"""

from typing import Dict, List, Optional


class StackSlot:
    """A slot on the stack frame"""
    def __init__(self, name: str, offset: int, size: int, alignment: int = 8):
        self.name = name
        self.offset = offset
        self.size = size
        self.alignment = alignment


class StackFrame:
    """Manages stack frame layout for a function"""
    
    def __init__(self, name: str):
        self.name = name
        self.local_offset = -8      # First local at RBP-8
        self.locals: Dict[str, StackSlot] = {}
        self.total_size = 0
    
    def allocate_local(self, name: str, size: int = 8, alignment: int = 8) -> StackSlot:
        """Allocate a local variable on the stack"""
        # Move offset down by size
        self.local_offset -= size
        # Align to requested alignment (8 bytes by default)
        self.local_offset -= (self.local_offset % alignment) if self.local_offset % alignment else 0
        
        slot = StackSlot(name, self.local_offset, size, alignment)
        self.locals[name] = slot
        
        # Update total size (positive number)
        self.total_size = max(self.total_size, abs(self.local_offset))
        return slot
    
    def get_local_offset(self, name: str) -> Optional[int]:
        """Get offset for a local variable"""
        if name in self.locals:
            return self.locals[name].offset
        return None
    
    def get_stack_size(self) -> int:
        """Get total stack frame size (aligned to 16 bytes)"""
        # Align to 16 bytes (required by ABI)
        return (self.total_size + 15) & ~15
    
    def get_prologue(self) -> List[str]:
        """Generate function prologue assembly"""
        lines = []
        lines.append("    push rbp")
        lines.append("    mov rbp, rsp")
        
        stack_size = self.get_stack_size()
        if stack_size > 0:
            lines.append(f"    sub rsp, {stack_size}")
        
        return lines
    
    def get_epilogue(self) -> List[str]:
        """Generate function epilogue assembly"""
        lines = []
        lines.append("    mov rsp, rbp")
        lines.append("    pop rbp")
        lines.append("    ret")
        return lines
    
    def __str__(self):
        lines = [f"Stack frame for {self.name}:"]
        lines.append(f"  Total size: {self.get_stack_size()} bytes")
        lines.append("  Locals:")
        for name, slot in self.locals.items():
            lines.append(f"    {name}: offset={slot.offset}, size={slot.size}")
        return "\n".join(lines)