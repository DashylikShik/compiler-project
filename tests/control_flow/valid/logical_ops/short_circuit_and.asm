section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 64
    mov dword [rbp-8], 0
    mov dword [rbp-16], 10
    mov eax, [rbp-8]
    cmp eax, 0
    setne al
    movzx eax, al
    mov dword [rbp-24], eax
    mov eax, [rbp-24]
    cmp eax, 0
    je L1
    mov eax, [rbp-16]
    cdq
    idiv dword [rbp-8]
    mov dword [rbp-32], eax
    mov eax, [rbp-32]
    cmp eax, 2
    setg al
    movzx eax, al
    mov dword [rbp-40], eax
    mov eax, [rbp-40]
    cmp eax, 0
    je L1
    mov dword [rbp-48], 1
    jmp L2

L1:
    mov dword [rbp-48], 0
    jmp L2

L2:
    mov eax, [rbp-48]
    cmp eax, 0
    jne L3
    jmp L4

L3:
    mov eax, 1
    mov rsp, rbp
    pop rbp
    ret

L4:
    jmp L5

L5:
    mov eax, 0
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
