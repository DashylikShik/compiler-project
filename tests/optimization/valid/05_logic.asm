section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    cmp True, 0
    je L1
    cmp False, 0
    je L1
    mov [rbp-8], 1
    jmp L2

L2:
    mov eax, [rbp-8]
    mov [rbp-16], eax
    cmp True, 0
    jne L3
    cmp False, 0
    jne L3
    mov [rbp-24], 0
    jmp L4

L3:
    mov [rbp-24], 1
    jmp L4

L4:
    mov eax, [rbp-24]
    mov [rbp-32], eax
    mov rax, [rbp-16]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
