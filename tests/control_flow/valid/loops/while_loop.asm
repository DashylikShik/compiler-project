section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov dword [rbp-8], 0
    mov dword [rbp-16], 0
    jmp L1

L1:
    mov eax, [rbp-8]
    cmp eax, 5
    setl al
    movzx eax, al
    mov dword [rbp-24], eax
    mov eax, [rbp-24]
    cmp eax, 0
    jne L2
    jmp L3

L2:
    mov eax, [rbp-16]
    add eax, [rbp-8]
    mov dword [rbp-32], eax
    mov eax, dword [rbp-32]
    mov dword [rbp-16], eax
    mov eax, [rbp-8]
    add eax, 1
    mov dword [rbp-40], eax
    mov eax, dword [rbp-40]
    mov dword [rbp-8], eax
    jmp L1

L3:
    mov eax, dword [rbp-16]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
