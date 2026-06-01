section .rodata
LC1: db 83, 112, 114, 105, 110, 116, 32, 56, 32, 101, 120, 116, 101, 114, 110, 97, 108, 32, 100, 101, 109, 111, 10, 0

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
    mov eax, 5
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
