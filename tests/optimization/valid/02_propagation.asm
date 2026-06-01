section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov dword [rbp-8], 5
    mov eax, dword [rbp-8]
    mov dword [rbp-16], eax
    mov eax, [rbp-16]
    add eax, 10
    mov dword [rbp-24], eax
    mov eax, dword [rbp-24]
    mov dword [rbp-32], eax
    mov eax, dword [rbp-32]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
