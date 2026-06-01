"""Basic block and control flow graph structures"""

from dataclasses import dataclass, field
from typing import List, Optional, Set
from .ir_instructions import Instruction, InstructionType, Operand


@dataclass
class BasicBlock:
    """Basic block - sequence of instructions with single entry/exit"""
    label: str
    instructions: List[Instruction] = field(default_factory=list)
    predecessors: List['BasicBlock'] = field(default_factory=list)
    successors: List['BasicBlock'] = field(default_factory=list)
    
    def add_instruction(self, instr: Instruction):
        self.instructions.append(instr)
    
    def is_terminated(self) -> bool:
        """Check if block ends with terminator instruction"""
        if not self.instructions:
            return False
        last = self.instructions[-1]
        return last.type in [
            InstructionType.JUMP,
            InstructionType.JUMP_IF,
            InstructionType.JUMP_IF_NOT,
            InstructionType.RETURN
        ]
    
    def get_label_operand(self) -> Operand:
        return Operand.label(self.label)
    
    def __str__(self):
        lines = [f"{self.label}:"]
        for instr in self.instructions:
            lines.append(str(instr))
        return "\n".join(lines)


class ControlFlowGraph:
    """Control flow graph for a function"""
    
    def __init__(self, blocks: List[BasicBlock]):
        self.blocks = blocks
        self._build_edges()
    
    def _build_edges(self):
        """Build predecessor/successor relationships"""
        block_map = {b.label: b for b in self.blocks}
        
        for block in self.blocks:
            if not block.instructions:
                continue
            
            last_instr = block.instructions[-1]
            
            if last_instr.type == InstructionType.JUMP:
                target_label = last_instr.src1.value
                if target_label in block_map:
                    target = block_map[target_label]
                    block.successors.append(target)
                    target.predecessors.append(block)
            
            elif last_instr.type in [InstructionType.JUMP_IF, InstructionType.JUMP_IF_NOT]:
                pass
    
    def dump(self) -> str:
        """Dump CFG as string"""
        lines = []
        for block in self.blocks:
            lines.append(str(block))
            if block.successors:
                succ_names = [s.label for s in block.successors]
                lines.append(f"  -> {', '.join(succ_names)}")
        return "\n".join(lines)