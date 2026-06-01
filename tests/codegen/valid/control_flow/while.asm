section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov [rbp-8], 0
    jmp L1

L1:
    mov eax, [rbp-8]
    cmp eax, 5
    setl al
    movzx eax, al
    mov [rbp-16], eax
    mov eax, [rbp-16]
    cmp eax, 0
    jne L2
    jmp L3

L2:
    mov eax, [rbp-8]
    add eax, 1
    mov [rbp-24], eax
    mov eax, [rbp-24]
    mov [rbp-8], eax
    jmp L1

L3:
    mov eax, dword [rbp-8]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
