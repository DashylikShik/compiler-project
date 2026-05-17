section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov [rbp-8], 5
    cmp [rbp-16], 0
    jne L1
    jmp L2

L1:
    mov rax, 1
    mov rsp, rbp
    pop rbp
    ret

L2:
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret

L3:
    mov rax, 0
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
