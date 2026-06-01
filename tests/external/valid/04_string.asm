section .rodata
LC1: db 104, 101, 108, 108, 111, 0

section .text
extern strlen
extern strcpy
extern malloc
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov rdi, 80
    call malloc
    mov qword [rbp-8], rax
    mov rdi, [rbp-8]
    lea rsi, [rel LC1]
    call strcpy
    mov qword [rbp-16], rax
    mov rdi, [rbp-8]
    call strlen
    mov qword [rbp-24], rax
    mov eax, dword [rbp-24]
    mov dword [rbp-32], eax
    mov eax, dword [rbp-32]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
