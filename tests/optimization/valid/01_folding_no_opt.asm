section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov eax, 2
    add eax, 3
    mov [rbp-8], eax
    mov eax, [rbp-8]
    mov [rbp-16], eax
    mov eax, 4
    imul eax, 5
    mov [rbp-24], eax
    mov eax, [rbp-24]
    mov [rbp-32], eax
    mov eax, [rbp-16]
    add eax, [rbp-32]
    mov [rbp-40], eax
    mov eax, dword [rbp-40]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
