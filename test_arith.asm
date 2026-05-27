section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov eax, 3
    imul eax, 4
    mov [rbp-8], eax
    mov eax, 2
    add eax, [rbp-8]
    mov [rbp-16], eax
    mov rax, [rbp-16]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
