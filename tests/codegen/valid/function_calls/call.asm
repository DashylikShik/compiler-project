section .text
global main


add:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov [rbp-16], [rbp-8]
    mov eax, [rbp-8]
    add eax, [rbp-16]
    mov [rbp-24], eax
    mov rax, [rbp-24]
    mov rsp, rbp
    pop rbp
    ret

main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov edi, 5
    mov esi, 3
    call add
    mov [rbp-8], eax
    mov rax, [rbp-8]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
