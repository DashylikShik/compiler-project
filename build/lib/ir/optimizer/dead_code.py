"""Dead code elimination optimization pass for Sprint 7"""

from ..ir_instructions import Instruction, InstructionType, Operand, IRProgram, IRFunction, BasicBlock


class DeadCodeElimination:
    """Removes unreachable blocks and dead code"""
    
    def __init__(self):
        self.removed_count = 0
        self.unused_vars = set()
    
    def optimize(self, program: IRProgram) -> IRProgram:
        self.removed_count = 0
        
        for func in program.functions:
            self.optimize_function(func)
        
        return program
    
    def optimize_function(self, func: IRFunction):
        """Remove unreachable basic blocks and dead code"""
        if not func.basic_blocks:
            return
        
        # Step 1: Mark reachable blocks
        reachable = set()
        worklist = [func.basic_blocks[0]]
        
        while worklist:
            block = worklist.pop()
            if block.label in reachable:
                continue
            reachable.add(block.label)
            
            for instr in block.instructions:
                if instr.type == InstructionType.JUMP and instr.src1:
                    target = instr.src1.value
                    for b in func.basic_blocks:
                        if b.label == target and b.label not in reachable:
                            worklist.append(b)
                            break
                elif instr.type == InstructionType.JUMP_IF and instr.src2:
                    target = instr.src2.value
                    for b in func.basic_blocks:
                        if b.label == target and b.label not in reachable:
                            worklist.append(b)
                            break
                elif instr.type == InstructionType.JUMP_IF_NOT and instr.src2:
                    target = instr.src2.value
                    for b in func.basic_blocks:
                        if b.label == target and b.label not in reachable:
                            worklist.append(b)
                            break
        
        # Step 2: Remove unreachable blocks
        new_blocks = [b for b in func.basic_blocks if b.label in reachable]
        removed = len(func.basic_blocks) - len(new_blocks)
        self.removed_count += removed
        func.basic_blocks = new_blocks
        
        # Step 3: Remove unused variable assignments (simple DCE)
        for block in func.basic_blocks:
            used_vars = set()
            # First pass: collect used variables
            for instr in block.instructions:
                if instr.src1 and instr.src1.operand_type == "temp":
                    used_vars.add(instr.src1.value)
                if instr.src2 and instr.src2.operand_type == "temp":
                    used_vars.add(instr.src2.value)
            
            # Second pass: remove unused assignments
            new_instrs = []
            for instr in block.instructions:
                if instr.type == InstructionType.MOVE:
                    if instr.dest and instr.dest.value not in used_vars:
                        # This assignment is never used
                        self.removed_count += 1
                        continue
                new_instrs.append(instr)
            block.instructions = new_instrs
    
    def get_stats(self):
        return {"dead_code_removed": self.removed_count}