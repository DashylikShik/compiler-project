section .text
extern free
extern malloc
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov rdi, 16
    call malloc
    mov [rbp-8], rax
    mov eax, [rbp-8]
    mov [rbp-16], eax
    mov rdi, [rbp-16]
    call free
    mov [rbp-24], rax
    mov eax, 0
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
