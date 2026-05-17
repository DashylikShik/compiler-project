section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov [rbp-8], 10
    mov [rbp-16], 20
    mov eax, [rbp-8]
    add eax, [rbp-16]
    mov [rbp-24], eax
    mov rax, [rbp-24]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
