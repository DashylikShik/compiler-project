"""x86-64 code generator from IR"""

from typing import List, Dict, Optional
from ir.ir_instructions import Instruction, InstructionType, Operand, IRFunction, IRProgram
from .abi import ABI
from .stack_frame import StackFrame


class X86Generator:
    """Generates x86-64 assembly from IR"""
    
    def __init__(self):
        self.sections = {
            'text': [],
            'data': [],
            'rodata': [],
            'bss': []
        }
        self.current_function: Optional[IRFunction] = None
        self.stack_frame: Optional[StackFrame] = None
        self.label_counter = 0
        self.temp_offset: Dict[str, int] = {}  # temp -> stack offset
        self.next_offset = -8
    
    def generate(self, program: IRProgram) -> str:
        """Generate assembly for entire IR program"""
        self.sections['text'] = []
        
        self.sections['text'].append("section .text")
        self.sections['text'].append("global main")
        self.sections['text'].append("")
        
        for func in program.functions:
            self.generate_function(func)
        
        self.generate_runtime_stubs()
        
        output = []
        for section in ['rodata', 'data', 'text']:
            if self.sections[section]:
                output.extend(self.sections[section])
                output.append("")
        
        return "\n".join(output)
    
    def generate_function(self, func: IRFunction):
        """Generate assembly for a function"""
        self.current_function = func
        self.stack_frame = StackFrame(func.name)
        self.temp_offset = {}
        self.next_offset = -8
        
        # First pass: collect all temporaries and allocate stack slots
        for block in func.basic_blocks:
            for instr in block.instructions:
                # Allocate for destination
                if instr.dest and instr.dest.operand_type == "temp":
                    name = instr.dest.value
                    if name not in self.temp_offset:
                        self.temp_offset[name] = self.next_offset
                        self.stack_frame.allocate_local(name, 8)
                        self.next_offset -= 8
                
                # Allocate for sources
                for src in [instr.src1, instr.src2]:
                    if src and src.operand_type == "temp":
                        name = src.value
                        if name not in self.temp_offset:
                            self.temp_offset[name] = self.next_offset
                            self.stack_frame.allocate_local(name, 8)
                            self.next_offset -= 8
        
        # Function label
        self.sections['text'].append(f"\n{func.name}:")
        
        # Prologue
        for line in self.stack_frame.get_prologue():
            self.sections['text'].append(line)
        
        # Generate code for each basic block
        for block in func.basic_blocks:
            self.generate_basic_block(block)
        
        # Epilogue if needed
        if self.sections['text']:
            last_instr = self.sections['text'][-1].strip()
            if not last_instr.startswith('ret'):
                for line in self.stack_frame.get_epilogue():
                    self.sections['text'].append(line)
    
    def generate_basic_block(self, block):
        """Generate assembly for a basic block"""
        if block.label != 'entry':
            self.sections['text'].append(f"\n{block.label}:")
        
        for instr in block.instructions:
            self.generate_instruction(instr)
    
    def generate_instruction(self, instr: Instruction):
        """Generate assembly for a single IR instruction"""
        if instr.type == InstructionType.ADD:
            self.gen_add(instr)
        elif instr.type == InstructionType.SUB:
            self.gen_sub(instr)
        elif instr.type == InstructionType.MUL:
            self.gen_mul(instr)
        elif instr.type == InstructionType.DIV:
            self.gen_div(instr)
        elif instr.type == InstructionType.MOVE:
            self.gen_move(instr)
        elif instr.type == InstructionType.RETURN:
            self.gen_return(instr)
        elif instr.type == InstructionType.JUMP:
            self.gen_jump(instr)
        elif instr.type == InstructionType.JUMP_IF:
            self.gen_jump_if(instr)
        elif instr.type == InstructionType.CALL:
            self.gen_call(instr)
        elif instr.type == InstructionType.PARAM:
            self.gen_param(instr)
    
    def get_operand(self, op: Operand) -> str:
        """Convert IR operand to assembly string"""
        if op is None:
            return "0"
        
        if op.operand_type == "const":
            return str(op.value)
        elif op.operand_type == "label":
            return op.value
        elif op.operand_type == "var":
            return f"[rbp-8]"  # временно
        elif op.operand_type == "temp":
            # Get stack offset for this temporary
            name = op.value
            if name in self.temp_offset:
                offset = self.temp_offset[name]
                return f"[rbp{offset:+d}]"
            return name
        
        return str(op)
    
    def gen_add(self, instr: Instruction):
        """Generate ADD instruction"""
        src1 = self.get_operand(instr.src1)
        src2 = self.get_operand(instr.src2)
        dest = self.get_operand(instr.dest)
        
        self.sections['text'].append(f"    mov eax, {src1}")
        self.sections['text'].append(f"    add eax, {src2}")
        self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_sub(self, instr: Instruction):
        """Generate SUB instruction"""
        src1 = self.get_operand(instr.src1)
        src2 = self.get_operand(instr.src2)
        dest = self.get_operand(instr.dest)
        
        self.sections['text'].append(f"    mov eax, {src1}")
        self.sections['text'].append(f"    sub eax, {src2}")
        self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_mul(self, instr: Instruction):
        """Generate MUL instruction"""
        src1 = self.get_operand(instr.src1)
        src2 = self.get_operand(instr.src2)
        dest = self.get_operand(instr.dest)
        
        self.sections['text'].append(f"    mov eax, {src1}")
        self.sections['text'].append(f"    imul eax, {src2}")
        self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_div(self, instr: Instruction):
        """Generate DIV instruction"""
        src1 = self.get_operand(instr.src1)
        src2 = self.get_operand(instr.src2)
        dest = self.get_operand(instr.dest)
        
        self.sections['text'].append(f"    mov eax, {src1}")
        self.sections['text'].append(f"    cdq")
        self.sections['text'].append(f"    idiv dword {src2}")
        self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_move(self, instr: Instruction):
        """Generate MOVE instruction"""
        src = self.get_operand(instr.src1)
        dest = self.get_operand(instr.dest)
        
        if src == dest:
            return
        self.sections['text'].append(f"    mov {dest}, {src}")
    
    def gen_return(self, instr: Instruction):
        """Generate RETURN instruction"""
        if instr.src1:
            src = self.get_operand(instr.src1)
            self.sections['text'].append(f"    mov rax, {src}")
        
        for line in self.stack_frame.get_epilogue():
            self.sections['text'].append(line)
    
    def gen_jump(self, instr: Instruction):
        """Generate unconditional JUMP"""
        target = instr.src1.value
        self.sections['text'].append(f"    jmp {target}")
    
    def gen_jump_if(self, instr: Instruction):
        """Generate conditional JUMP_IF"""
        cond = self.get_operand(instr.src1)
        target = instr.src2.value
        
        self.sections['text'].append(f"    cmp {cond}, 0")
        self.sections['text'].append(f"    jne {target}")
    
    def gen_call(self, instr: Instruction):
        """Generate CALL instruction"""
        func_name = instr.src1.value
        self.sections['text'].append(f"    call {func_name}")
        
        if instr.dest:
            dest = self.get_operand(instr.dest)
            self.sections['text'].append(f"    mov {dest}, eax")

    def gen_param(self, instr: Instruction):
        """Generate PARAM instruction"""
        index = int(instr.src1.value) if instr.src1 else 0
        value = self.get_operand(instr.src2)
        
        # System V ABI: первые 6 целочисленных аргументов в RDI, RSI, RDX, RCX, R8, R9
        registers_64 = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
        registers_32 = ['edi', 'esi', 'edx', 'ecx', 'r8d', 'r9d']
        
        if index < len(registers_64):
            # Используем 32-битные регистры для тестов
            reg = registers_32[index]
            self.sections['text'].append(f"    mov {reg}, {value}")
        else:
            self.sections['text'].append(f"    push {value}")
    
    def generate_runtime_stubs(self):
        """Generate runtime library stubs"""
        self.sections['text'].append("")
        self.sections['text'].append("exit:")
        self.sections['text'].append("    mov rax, 60")
        self.sections['text'].append("    syscall")