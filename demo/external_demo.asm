section .rodata
LC1: db 83, 112, 114, 105, 110, 116, 32, 55, 32, 101, 120, 116, 101, 114, 110, 97, 108, 32, 100, 101, 109, 111, 10, 0
LC2: db 104, 101, 108, 108, 111, 0

section .text
extern strlen
extern free
extern malloc
extern printf
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 64
    lea rdi, [rel LC1]
    xor eax, eax
    call printf
    mov [rbp-8], rax
    mov rdi, 4
    call malloc
    mov [rbp-16], rax
    mov eax, [rbp-16]
    mov [rbp-24], eax
    mov eax, [rbp-24]
    cmp eax, 0
    setne al
    movzx eax, al
    mov [rbp-32], eax
    mov eax, [rbp-32]
    cmp eax, 0
    jne L1
    jmp L2

L1:
    mov rdi, [rbp-24]
    call free
    mov [rbp-40], rax
    jmp L3

L2:
    jmp L3

L3:
    lea rdi, [rel LC2]
    call strlen
    mov [rbp-48], rax
    mov eax, [rbp-48]
    mov [rbp-56], eax
    mov eax, dword [rbp-56]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
