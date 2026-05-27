section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 64
    mov [rbp-8], 0
    mov [rbp-16], 10
    cmp [rbp-24], 0
    je L1
    mov eax, [rbp-16]
    cdq
    idiv dword [rbp-8]
    mov [rbp-32], eax
    mov eax, [rbp-32]
    cmp eax, 2
    setg al
    movzx eax, al
    mov [rbp-40], eax
    cmp [rbp-40], 0
    je L1
    mov [rbp-48], 1
    jmp L2

L1:
    mov [rbp-48], 0
    jmp L2

L2:
    cmp [rbp-48], 0
    jne L3
    jmp L4

L3:
    mov rax, 1
    mov rsp, rbp
    pop rbp
    ret

L4:
    jmp L5

L5:
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
