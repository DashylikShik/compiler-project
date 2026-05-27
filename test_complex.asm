section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 96
    mov [rbp-8], 0
    mov [rbp-16], 1
    jmp L1

L1:
    cmp [rbp-24], 0
    jne L2
    jmp L4

L2:
    mov [rbp-32], 1
    jmp L5

L5:
    cmp [rbp-40], 0
    jne L6
    jmp L8

L6:
    mov eax, [rbp-16]
    cmp eax, [rbp-32]
    sete al
    movzx eax, al
    mov [rbp-48], eax
    cmp [rbp-48], 0
    jne L9
    jmp L10

L9:
    mov eax, [rbp-16]
    imul eax, [rbp-32]
    mov [rbp-56], eax
    mov eax, [rbp-8]
    add eax, [rbp-56]
    mov [rbp-64], eax
    mov eax, [rbp-64]
    mov [rbp-8], eax
    jmp L11

L10:
    jmp L11

L11:
    jmp L7

L7:
    mov eax, [rbp-32]
    add eax, 1
    mov [rbp-72], eax
    mov eax, [rbp-72]
    mov [rbp-32], eax
    jmp L5

L8:
    jmp L3

L3:
    mov eax, [rbp-16]
    add eax, 1
    mov [rbp-80], eax
    mov eax, [rbp-80]
    mov [rbp-16], eax
    jmp L1

L4:
    mov rax, [rbp-8]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
