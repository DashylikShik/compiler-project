section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov [rbp-8], 5
    mov eax, [rbp-8]
    mov [rbp-16], eax
    mov eax, [rbp-16]
    add eax, 10
    mov [rbp-24], eax
    mov eax, [rbp-24]
    mov [rbp-32], eax
    mov eax, dword [rbp-32]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
