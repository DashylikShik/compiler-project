section .text
global main


main:
    push rbp
    mov rbp, rsp
    mov rax, 42
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
