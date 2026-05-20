section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov [rbp-8], 5
    mov [rbp-16], 10
    mov eax, [rbp-8]
    cmp eax, 0
    setg al
    movzx eax, al
    mov [rbp-24], eax
    mov eax, [rbp-16]
    cmp eax, 5
    setg al
    movzx eax, al
    mov [rbp-32], eax
    mov eax, [rbp-24]
    cmp eax, 0
    je L_false1
    mov eax, [rbp-32]
    cmp eax, 0
    je L_false1
    mov eax, 1
    jmp L_end2
L_false1:
    mov eax, 0
L_end2:
    mov [rbp-40], eax
    cmp [rbp-40], 0
    jne L1
    jmp L2

L1:
    mov rax, 1
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
