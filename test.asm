section .text
global main


main:
    push rbp
    mov rbp, rsp
    mov rax, 42
    mov rsp, rbp
    pop rbp
    ret

; Runtime library stubs

exit:
    mov rax, 60
    syscall
    ret
