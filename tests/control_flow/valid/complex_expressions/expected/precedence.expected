section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov dword [rbp-8], 2
    mov dword [rbp-16], 3
    mov dword [rbp-24], 4
    mov eax, [rbp-16]
    imul eax, [rbp-24]
    mov dword [rbp-32], eax
    mov eax, [rbp-8]
    add eax, [rbp-32]
    mov dword [rbp-40], eax
    mov eax, dword [rbp-40]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
