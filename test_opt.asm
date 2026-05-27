section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 64
    mov [rbp-8], 5
    mov eax, [rbp-8]
    mov [rbp-16], eax
    mov [rbp-24], 20
    mov eax, [rbp-24]
    mov [rbp-32], eax
    mov eax, [rbp-16]
    cmp eax, [rbp-32]
    setg al
    movzx eax, al
    mov [rbp-40], eax
    cmp [rbp-40], 0
    jne L1
    jmp L2

L1:
    mov rax, 100
    mov rsp, rbp
    pop rbp
    ret

L2:
    mov eax, [rbp-16]
    add eax, [rbp-32]
    mov [rbp-48], eax
    mov rax, [rbp-48]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
