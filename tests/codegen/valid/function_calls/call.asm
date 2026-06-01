section .text
global main


add:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov [rbp-8], rdi
    mov [rbp-16], rsi
    mov eax, [rbp-8]
    add eax, [rbp-16]
    mov [rbp-24], eax
    mov eax, dword [rbp-24]
    mov rsp, rbp
    pop rbp
    ret

main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov rdi, 5
    mov rsi, 3
    call add
    mov [rbp-8], rax
    mov eax, dword [rbp-8]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
