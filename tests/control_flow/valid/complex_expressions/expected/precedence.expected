section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov [rbp-8], 2
    mov [rbp-16], 3
    mov [rbp-24], 4
    mov eax, [rbp-16]
    imul eax, [rbp-24]
    mov [rbp-32], eax
    mov eax, [rbp-8]
    add eax, [rbp-32]
    mov [rbp-40], eax
    mov rax, [rbp-40]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
