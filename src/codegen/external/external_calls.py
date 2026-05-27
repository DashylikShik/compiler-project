"""External function calls (C library integration) for Sprint 7"""

class ExternalCallGenerator:
    """Generates assembly for external function calls following System V AMD64 ABI"""
    
    def __init__(self, sections):
        self.sections = sections
        self.extern_declared = set()
    
    def declare_extern(self, func_name: str):
        """Declare external function"""
        if func_name not in self.extern_declared:
            self.sections['text'].insert(0, f"extern {func_name}")
            self.extern_declared.add(func_name)
    
    def generate_call(self, func_name: str, args: list, is_variadic: bool = False) -> str:
        """Generate call to external function following System V ABI"""
        self.declare_extern(func_name)
        
        # Save caller-saved registers
        self.sections['text'].append("    push rax")
        self.sections['text'].append("    push rcx")
        self.sections['text'].append("    push rdx")
        
        # Integer argument registers: RDI, RSI, RDX, RCX, R8, R9
        int_regs = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']
        
        for i, arg in enumerate(args[:6]):
            self.sections['text'].append(f"    mov {int_regs[i]}, {arg}")
        
        # Push remaining arguments to stack (right-to-left order)
        for i in range(len(args) - 1, 5, -1):
            self.sections['text'].append(f"    push {args[i]}")
        
        # For variadic functions, set AL to number of vector registers used
        if is_variadic:
            self.sections['text'].append("    xor eax, eax")
        
        # Make the call
        self.sections['text'].append(f"    call {func_name}")
        
        # Clean up stack if we pushed arguments
        if len(args) > 6:
            stack_cleanup = (len(args) - 6) * 8
            self.sections['text'].append(f"    add rsp, {stack_cleanup}")
        
        # Restore caller-saved registers
        self.sections['text'].append("    pop rdx")
        self.sections['text'].append("    pop rcx")
        self.sections['text'].append("    pop rax")
        
        return "eax"