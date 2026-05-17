section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov eax, 2
    add eax, 3
    mov [rbp-8], eax
    mov rax, [rbp-8]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
