section .rodata
LC1: db 72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100, 33, 10, 0

section .text
extern printf
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    lea rdi, [rel LC1]
    xor eax, eax
    call printf
    mov qword [rbp-8], rax
    mov eax, 0
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
