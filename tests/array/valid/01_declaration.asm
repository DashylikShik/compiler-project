section .text
extern malloc
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov rdi, 20
    call malloc
    mov qword [rbp-8], rax
    mov eax, 0
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
