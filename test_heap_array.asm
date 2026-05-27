section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 80
    mov eax, 5
    imul eax, 4
    mov [rbp-8], eax
    mov edi, [rbp-8]
    extern malloc
    call malloc
    mov [rbp-16], eax
    mov eax, [rbp-16]
    mov [rbp-24], eax
    cmp [rbp-32], 0
    jne L1
    jmp L2

L1:
    mov eax, 0
    add eax, 0
    mov [rbp-40], eax
    mov eax, [rbp-40]
    add eax, 0
    mov [rbp-48], eax
    mov eax, [rbp-48]
    mov [rbp-56], eax
    mov edi, [rbp-24]
    extern free
    call free
    mov [rbp-64], eax
    mov rax, [rbp-56]
    mov rsp, rbp
    pop rbp
    ret

L2:
    jmp L3

L3:
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
