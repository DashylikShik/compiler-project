"""Heap-based array code generation for Sprint 7.

Local arrays are represented as pointers.  The storage itself is allocated in
heap memory by malloc(size * element_size), not by ALLOCA/stack allocation.
"""

class ArrayGenerator:
    def __init__(self, sections, stack_frame=None, temp_offset=None):
        self.sections = sections
        self.stack_frame = stack_frame
        self.temp_offset = temp_offset or {}
        self.extern_declared = set()

    def declare_extern(self, name: str):
        if name not in self.extern_declared:
            insert_at = 1 if self.sections.get('text') and self.sections['text'][0].startswith('section') else 0
            self.sections['text'].insert(insert_at, f"extern {name}")
            self.extern_declared.add(name)

    def allocate_array(self, name: str, count: int, element_size: int = 4) -> str:
        """Allocate exactly count * element_size bytes in heap. Returns pointer in rax."""
        total_size = int(count) * int(element_size)
        self.declare_extern('malloc')
        self.sections['text'].append(f"    mov rdi, {total_size}    ; {name}: {count} * {element_size} bytes")
        self.sections['text'].append("    call malloc")
        return "rax"

    def generate_array_access(self, base: str, index: str, element_size: int, dest: str):
        self.sections['text'].append(f"    mov r10, {base}")
        self.sections['text'].append(f"    movsxd r11, dword {index}" if str(index).startswith('[') else f"    mov r11, {index}")
        if element_size != 1:
            self.sections['text'].append(f"    imul r11, {element_size}")
        self.sections['text'].append("    add r10, r11")
        self.sections['text'].append(f"    mov eax, dword [r10]")
        self.sections['text'].append(f"    mov {dest}, eax")

    def generate_array_store(self, base: str, index: str, value: str, element_size: int):
        self.sections['text'].append(f"    mov r10, {base}")
        self.sections['text'].append(f"    movsxd r11, dword {index}" if str(index).startswith('[') else f"    mov r11, {index}")
        if element_size != 1:
            self.sections['text'].append(f"    imul r11, {element_size}")
        self.sections['text'].append("    add r10, r11")
        self.sections['text'].append(f"    mov eax, {value}")
        self.sections['text'].append("    mov dword [r10], eax")
