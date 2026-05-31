"""External function calls for Sprint 7"""

class ExternalCallGenerator:
    def __init__(self, sections):
        self.sections = sections
        self.extern_declared = set()

    def declare_extern(self, func_name: str):
        if func_name not in self.extern_declared:
            insert_at = 1 if self.sections.get('text') and self.sections['text'][0].startswith('section') else 0
            self.sections['text'].insert(insert_at, f"extern {func_name}")
            self.extern_declared.add(func_name)

    def generate_call(self, func_name: str, args: list, is_variadic: bool = False) -> str:
        self.declare_extern(func_name)

        regs = ['rdi', 'rsi', 'rdx', 'rcx', 'r8', 'r9']

        for i, arg in enumerate(args[:6]):
            self.sections['text'].append(f"    mov {regs[i]}, {arg}")

        for arg in reversed(args[6:]):
            self.sections['text'].append(f"    push {arg}")

        if is_variadic:
            self.sections['text'].append("    xor eax, eax")

        self.sections['text'].append(f"    call {func_name}")

        if len(args) > 6:
            self.sections['text'].append(f"    add rsp, {(len(args) - 6) * 8}")

        return "rax"