; runtime.asm - Minimal runtime library for MiniCompiler
; System V AMD64 ABI for Linux

section .text
global print_int
global print_string
global exit
global _start

; print_int(rdi: integer) -> void
; Prints integer to stdout
print_int:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    
    mov [rbp-8], rdi        ; save number
    mov rax, rdi
    mov rcx, 10
    mov rbx, 0
    mov rsi, rsp
    add rsi, 32
    
.loop:
    xor rdx, rdx
    div rcx
    add dl, '0'
    dec rsi
    mov [rsi], dl
    inc rbx
    test rax, rax
    jnz .loop
    
    ; write syscall
    mov rax, 1              ; sys_write
    mov rdi, 1              ; stdout
    mov rdx, rbx            ; length
    syscall
    
    mov rsp, rbp
    pop rbp
    ret

; print_string(rdi: string) -> void
; Prints null-terminated string to stdout
print_string:
    push rbp
    mov rbp, rsp
    push rdi
    
    mov rsi, rdi            ; string pointer
    xor rdx, rdx            ; length = 0
.length_loop:
    cmp byte [rsi + rdx], 0
    je .done
    inc rdx
    jmp .length_loop
.done:
    mov rax, 1              ; sys_write
    mov rdi, 1              ; stdout
    syscall
    
    pop rdi
    pop rbp
    ret

; exit(rdi: code) -> void
exit:
    mov rax, 60             ; sys_exit
    syscall
    ; No return

; _start - program entry point
_start:
    call main
    mov rdi, rax
    call exit