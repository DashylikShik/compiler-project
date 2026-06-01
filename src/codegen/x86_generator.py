"""x86-64 code generator from IR with control flow support"""

from typing import List, Dict, Optional
from ir.ir_instructions import Instruction, InstructionType, Operand, IRFunction, IRProgram
from .abi import ABI
from .stack_frame import StackFrame
from .label_manager import LabelManager
from .control_flow_generator import ControlFlowGenerator
from .external.external_calls import ExternalCallGenerator
from .array.array_generator import ArrayGenerator


class X86Generator:
    """Generates x86-64 assembly from IR with control flow support"""
    
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
        self.temp_offset: Dict[str, int] = {}
        self.next_offset = -8
        self.label_manager = LabelManager()
        self.cf_generator = None
        self.current_block_instrs = []  # временное хранилище для инструкций блока
        self.extern_declared = set()
        self.string_literals = {}
        self.string_counter = 0
        self.external = ExternalCallGenerator(self.sections)
        self.array_gen = ArrayGenerator(self.sections)
    
    def generate(self, program: IRProgram) -> str:
        """Generate assembly for entire IR program"""
        self.sections['text'] = []
        self.sections['rodata'] = []
        self.extern_declared = set()
        self.string_literals = {}
        self.string_counter = 0
        self.external = ExternalCallGenerator(self.sections)
        self.array_gen = ArrayGenerator(self.sections)
        
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
        self.label_manager.reset()
        self.cf_generator = ControlFlowGenerator(self.label_manager)
        
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
        elif instr.type == InstructionType.JUMP_IF_NOT:
            self.gen_jump_if_not(instr)
        elif instr.type == InstructionType.CALL:
            self.gen_call(instr)
        elif instr.type == InstructionType.PARAM:
            self.gen_param(instr)
        elif instr.type == InstructionType.LABEL:
            self.gen_label(instr)
        elif instr.type == InstructionType.AND:
            self.gen_logical_and(instr)
        elif instr.type == InstructionType.OR:
            self.gen_logical_or(instr)
        elif instr.type == InstructionType.NOT:
            self.gen_logical_not(instr)
        elif instr.type == InstructionType.CMP_EQ:
            self.gen_cmp_eq(instr)
        elif instr.type == InstructionType.CMP_LT:
            self.gen_cmp_lt(instr)
        elif instr.type == InstructionType.CMP_GT:
            self.gen_cmp_gt(instr)
        elif instr.type == InstructionType.CMP_NE:
            self.gen_cmp_ne(instr)
        elif instr.type == InstructionType.CMP_LE:
            self.gen_cmp_le(instr)
        elif instr.type == InstructionType.CMP_GE:
            self.gen_cmp_ge(instr)
        elif instr.type == InstructionType.ARRAY_LOAD:
            self.gen_array_load(instr)
        elif instr.type == InstructionType.ARRAY_STORE:
            self.gen_array_store(instr)
    
    def declare_extern_once(self, name: str):
        if name not in self.extern_declared:
            insert_at = 1 if self.sections['text'] and self.sections['text'][0].startswith('section') else 0
            self.sections['text'].insert(insert_at, f"extern {name}")
            self.extern_declared.add(name)

    def get_string_label(self, value: str) -> str:
        value = value.replace('\\n', '\n').replace('\\t', '\t').replace('\\0', '\0')
        if value not in self.string_literals:
            self.string_counter += 1
            label = f"LC{self.string_counter}"
            self.string_literals[value] = label
            if not self.sections['rodata']:
                self.sections['rodata'].append("section .rodata")
            escaped = []
            for ch in value:
                if ch == '\\n':
                    escaped.append('10')
                elif ch == '\\t':
                    escaped.append('9')
                else:
                    escaped.append(str(ord(ch)))
            escaped.append('0')
            self.sections['rodata'].append(f"{label}: db {', '.join(escaped)}")
        return self.string_literals[value]

    def is_memory(self, asm: str) -> bool:
        return isinstance(asm, str) and asm.startswith('[')
    
    def needs_call_alignment_padding(self) -> bool:
        # next_offset начинается с -8 и уменьшается на 8 за каждый temp.
        # Размер локального фрейма примерно abs(next_offset + 8).
        local_size = abs(self.next_offset + 8)

        # После push rbp стек смещён на 8.
        # Перед call надо, чтобы rsp был кратен 16.
        return local_size % 16 == 0

    def get_operand(self, op: Operand) -> str:
        """Convert IR operand to assembly string.

        Temps are 8-byte stack slots, so pointer values from malloc are always
        stored/loaded as RAX-width values, not truncated to EAX.
        """
        if op is None:
            return "0"

        if op.operand_type == "const":
            if isinstance(op.value, str):
                return f"rel {self.get_string_label(op.value)}"
            return str(int(op.value)) if isinstance(op.value, bool) else str(op.value)
        elif op.operand_type == "label":
            return op.value
        elif op.operand_type == "var":
            # Function parameters initially live in ABI registers.
            if self.current_function:
                for idx, (pname, _ptype) in enumerate(self.current_function.parameters):
                    if pname == op.value:
                        regs = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
                        if idx < len(regs):
                            return regs[idx]
            offset = self.stack_frame.get_local_offset(op.value) if self.stack_frame else None
            if offset is not None:
                return f"[rbp{offset:+d}]"
            return op.value
        elif op.operand_type == "temp":
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
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_sub(self, instr: Instruction):
        """Generate SUB instruction"""
        src1 = self.get_operand(instr.src1)
        src2 = self.get_operand(instr.src2)
        dest = self.get_operand(instr.dest)
        
        self.sections['text'].append(f"    mov eax, {src1}")
        self.sections['text'].append(f"    sub eax, {src2}")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_mul(self, instr: Instruction):
        """Generate MUL instruction"""
        src1 = self.get_operand(instr.src1)
        src2 = self.get_operand(instr.src2)
        dest = self.get_operand(instr.dest)
        
        self.sections['text'].append(f"    mov eax, {src1}")
        self.sections['text'].append(f"    imul eax, {src2}")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_div(self, instr: Instruction):
        """Generate DIV instruction"""
        src1 = self.get_operand(instr.src1)
        src2 = self.get_operand(instr.src2)
        dest = self.get_operand(instr.dest)
        
        self.sections['text'].append(f"    mov eax, {src1}")
        self.sections['text'].append(f"    cdq")
        self.sections['text'].append(f"    idiv dword {src2}")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_move(self, instr: Instruction):
        """Generate MOVE instruction"""
        src = self.get_operand(instr.src1)
        dest = self.get_operand(instr.dest)
        
        if src == dest:
            return
        
        if src.startswith('[') and dest.startswith('['):
            self.sections['text'].append(f"    mov eax, dword {src}")
            self.sections['text'].append(f"    mov dword {dest}, eax")

        elif dest.startswith('['):
            if str(src).lstrip('-').isdigit():
                self.sections['text'].append(f"    mov dword {dest}, {src}")
            elif src == "eax":
                self.sections['text'].append(f"    mov dword {dest}, eax")
            elif src == "rax":
                self.sections['text'].append(f"    mov qword {dest}, rax")
            else:
                self.sections['text'].append(f"    mov qword {dest}, {src}")

        else:
            self.sections['text'].append(f"    mov {dest}, {src}")
    
    def gen_return(self, instr: Instruction):
        """Generate RETURN instruction"""
        if instr.src1:
            src = self.get_operand(instr.src1)
            if self.is_memory(src):
                self.sections['text'].append(f"    mov eax, dword {src}")
            else:
                self.sections['text'].append(f"    mov eax, {src}")

        for line in self.stack_frame.get_epilogue():
            self.sections['text'].append(line)
    
    def gen_jump(self, instr: Instruction):
        """Generate unconditional JUMP"""
        target = instr.src1.value
        self.sections['text'].append(f"    jmp {target}")
    
    def gen_jump_if(self, instr: Instruction):
        cond = self.get_operand(instr.src1)
        target = instr.src2.value

        self.sections['text'].append(f"    mov eax, {cond}")
        self.sections['text'].append("    cmp eax, 0")
        self.sections['text'].append(f"    jne {target}")
    
    def gen_jump_if_not(self, instr: Instruction):
        cond = self.get_operand(instr.src1)
        target = instr.src2.value

        self.sections['text'].append(f"    mov eax, {cond}")
        self.sections['text'].append("    cmp eax, 0")
        self.sections['text'].append(f"    je {target}")
    
    def gen_label(self, instr: Instruction):
        """Generate LABEL instruction"""
        if instr.label:
            self.sections['text'].append(f"{instr.label}:")
    
    def gen_logical_and(self, instr: Instruction):
        """Generate short-circuit AND (&&) with correct ordering"""
        # Получаем левый операнд
        left = self.get_operand(instr.src1)
        dest = self.get_operand(instr.dest)
        
        false_label = self.label_manager.new_label("L_false")
        end_label = self.label_manager.new_label("L_end")
        
        # Проверяем левый операнд
        self.sections['text'].append(f"    mov eax, {left}")
        self.sections['text'].append(f"    cmp eax, 0")
        self.sections['text'].append(f"    je {false_label}")
        
        # Правый операнд - ВАЖНО: он должен быть вычислен здесь!
        # Но в IR он уже вычислен, поэтому просто проверяем его значение
        right = self.get_operand(instr.src2)
        
        self.sections['text'].append(f"    mov eax, {right}")
        self.sections['text'].append(f"    cmp eax, 0")
        self.sections['text'].append(f"    je {false_label}")
        
        # Результат true
        self.sections['text'].append(f"    mov eax, 1")
        self.sections['text'].append(f"    jmp {end_label}")
        
        # Результат false
        self.sections['text'].append(f"{false_label}:")
        self.sections['text'].append(f"    mov eax, 0")
        
        self.sections['text'].append(f"{end_label}:")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_logical_or(self, instr: Instruction):
        """Generate short-circuit OR (||) with correct ordering"""
        left = self.get_operand(instr.src1)
        dest = self.get_operand(instr.dest)
        
        true_label = self.label_manager.new_label("L_true")
        end_label = self.label_manager.new_label("L_end")
        
        # Проверяем левый операнд
        self.sections['text'].append(f"    mov eax, {left}")
        self.sections['text'].append(f"    cmp eax, 0")
        self.sections['text'].append(f"    jne {true_label}")
        
        # Правый операнд
        right = self.get_operand(instr.src2)
        
        self.sections['text'].append(f"    mov eax, {right}")
        self.sections['text'].append(f"    cmp eax, 0")
        self.sections['text'].append(f"    jne {true_label}")
        
        # Результат false
        self.sections['text'].append(f"    mov eax, 0")
        self.sections['text'].append(f"    jmp {end_label}")
        
        # Результат true
        self.sections['text'].append(f"{true_label}:")
        self.sections['text'].append(f"    mov eax, 1")
        
        self.sections['text'].append(f"{end_label}:")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_logical_not(self, instr: Instruction):
        """Generate NOT (!) instruction"""
        src = self.get_operand(instr.src1)
        dest = self.get_operand(instr.dest)
        
        self.sections['text'].append(f"    mov eax, {src}")
        self.sections['text'].append(f"    cmp eax, 0")
        self.sections['text'].append(f"    sete al")
        self.sections['text'].append(f"    movzx eax, al")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_cmp_eq(self, instr: Instruction):
        """Generate equality comparison (==)"""
        left = self.get_operand(instr.src1)
        right = self.get_operand(instr.src2)
        dest = self.get_operand(instr.dest)
        
        self.sections['text'].append(f"    mov eax, {left}")
        self.sections['text'].append(f"    cmp eax, {right}")
        self.sections['text'].append(f"    sete al")
        self.sections['text'].append(f"    movzx eax, al")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")
            
    def gen_cmp_lt(self, instr: Instruction):
        """Generate less than comparison (<)"""
        left = self.get_operand(instr.src1)
        right = self.get_operand(instr.src2)
        dest = self.get_operand(instr.dest)
        
        self.sections['text'].append(f"    mov eax, {left}")
        self.sections['text'].append(f"    cmp eax, {right}")
        self.sections['text'].append(f"    setl al")
        self.sections['text'].append(f"    movzx eax, al")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_cmp_gt(self, instr: Instruction):
        """Generate greater than comparison (>)"""
        left = self.get_operand(instr.src1)
        right = self.get_operand(instr.src2)
        dest = self.get_operand(instr.dest)
        
        self.sections['text'].append(f"    mov eax, {left}")
        self.sections['text'].append(f"    cmp eax, {right}")
        self.sections['text'].append(f"    setg al")
        self.sections['text'].append(f"    movzx eax, al")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")
    
    def gen_cmp_ne(self, instr: Instruction):
        left = self.get_operand(instr.src1); right = self.get_operand(instr.src2); dest = self.get_operand(instr.dest)
        self.sections['text'].append(f"    mov eax, {left}")
        self.sections['text'].append(f"    cmp eax, {right}")
        self.sections['text'].append("    setne al")
        self.sections['text'].append("    movzx eax, al")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")

    def gen_cmp_le(self, instr: Instruction):
        left = self.get_operand(instr.src1); right = self.get_operand(instr.src2); dest = self.get_operand(instr.dest)
        self.sections['text'].append(f"    mov eax, {left}")
        self.sections['text'].append(f"    cmp eax, {right}")
        self.sections['text'].append("    setle al")
        self.sections['text'].append("    movzx eax, al")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")

    def gen_cmp_ge(self, instr: Instruction):
        left = self.get_operand(instr.src1); right = self.get_operand(instr.src2); dest = self.get_operand(instr.dest)
        self.sections['text'].append(f"    mov eax, {left}")
        self.sections['text'].append(f"    cmp eax, {right}")
        self.sections['text'].append("    setge al")
        self.sections['text'].append("    movzx eax, al")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov dword {dest}, eax")
        else:
            self.sections['text'].append(f"    mov {dest}, eax")

    def gen_array_load(self, instr: Instruction):
        base = self.get_operand(instr.src1)
        index = self.get_operand(instr.src2)
        dest = self.get_operand(instr.dest)
        self.sections['text'].append(f"    mov r10, {base}")
        self.sections['text'].append(f"    movsxd r11, dword {index}" if self.is_memory(index) else f"    mov r11, {index}")
        self.sections['text'].append("    shl r11, 2")
        self.sections['text'].append("    add r10, r11")
        self.sections['text'].append("    mov eax, dword [r10]")
        if dest.startswith('['):
            self.sections['text'].append(f"    mov qword {dest}, rax")
        else:
            self.sections['text'].append(f"    mov {dest}, rax")

    def gen_array_store(self, instr: Instruction):
        base = self.get_operand(instr.dest)
        index = self.get_operand(instr.src1)
        value = self.get_operand(instr.src2)
        self.sections['text'].append(f"    mov r10, {base}")
        self.sections['text'].append(f"    movsxd r11, dword {index}" if self.is_memory(index) else f"    mov r11, {index}")
        self.sections['text'].append("    shl r11, 2")
        self.sections['text'].append("    add r10, r11")
        self.sections['text'].append(f"    mov eax, {value}")
        self.sections['text'].append("    mov dword [r10], eax")

    def gen_call(self, instr: Instruction):
        """Generate CALL instruction with System V ABI support."""
        func_name = instr.src1.value

        extern_funcs = {
            'printf', 'scanf', 'malloc', 'free', 'puts', 'getchar',
            'memcpy', 'memset', 'pow', 'sqrt', 'sin', 'cos',
            'strlen', 'strcpy', 'strcmp'
        }

        if func_name in extern_funcs:
            self.declare_extern_once(func_name)

        if func_name in {'printf', 'scanf'}:
            self.sections['text'].append("    xor eax, eax")

        self.sections['text'].append(f"    call {func_name}")

        if instr.dest:
            dest = self.get_operand(instr.dest)
            if dest.startswith('['):
                self.sections['text'].append(f"    mov qword {dest}, rax")
            else:
                self.sections['text'].append(f"    mov {dest}, rax")

    def gen_param(self, instr: Instruction):
        """Generate PARAM instruction. Integer and pointer args use 64-bit ABI regs."""
        index = int(instr.src1.value) if instr.src1 else 0
        value = self.get_operand(instr.src2)
        regs = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
        if index < len(regs):
            reg = regs[index]
            if isinstance(value, str) and value.startswith('rel '):
                self.sections['text'].append(f"    lea {reg}, [{value}]")
            else:
                self.sections['text'].append(f"    mov {reg}, {value}")
        else:
            self.sections['text'].append(f"    push {value}")

    def gen_malloc(self, size: str) -> str:
        """Generate call to malloc"""
        self.sections['text'].append("    extern malloc")
        self.sections['text'].append(f"    mov rdi, {size}")
        self.sections['text'].append("    call malloc")
        return "rax"

    def gen_free(self, ptr: str):
        """Generate call to free"""
        self.sections['text'].append("    extern free")
        self.sections['text'].append(f"    mov rdi, {ptr}")
        self.sections['text'].append("    call free")

    def gen_array_access(self, base: str, index: str, element_size: int = 4) -> str:
        """Generate array element access: base + index * element_size"""
        temp_reg = "r10"
        self.sections['text'].append(f"    mov {temp_reg}, {base}")
        self.sections['text'].append(f"    mov r11, {index}")
        self.sections['text'].append(f"    imul r11, {element_size}")
        self.sections['text'].append(f"    add {temp_reg}, r11")
        return f"[{temp_reg}]"


    def generate_runtime_stubs(self):
        """Generate runtime library stubs"""
        self.sections['text'].append("")
        self.sections['text'].append("exit:")
        self.sections['text'].append("    mov rax, 60")
        self.sections['text'].append("    syscall")