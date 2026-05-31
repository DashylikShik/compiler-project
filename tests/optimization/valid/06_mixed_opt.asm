section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov [rbp-8], 5
    mov eax, [rbp-8]
    mov [rbp-16], eax
    mov eax, [rbp-16]
    imul eax, 2
    mov [rbp-24], eax
    mov eax, [rbp-24]
    mov [rbp-32], eax
    mov eax, [rbp-32]
    cmp eax, 10
    setg al
    movzx eax, al
    mov [rbp-40], eax
    mov eax, [rbp-40]
    cmp eax, 0
    jne L1
    jmp L2

L1:
    mov eax, 100
    mov rsp, rbp
    pop rbp
    ret

L2:
    mov eax, dword [rbp-32]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
