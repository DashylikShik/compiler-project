section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov eax, 1
    cmp eax, 0
    je L1
    mov eax, 0
    cmp eax, 0
    je L1
    jmp L2

L1:
    jmp L2

L2:
    mov eax, 1
    cmp eax, 0
    jne L3
    mov eax, 0
    cmp eax, 0
    jne L3
    jmp L4

L3:
    jmp L4

L4:
    mov eax, dword [rbp-8]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
