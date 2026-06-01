section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov eax, 5
    cmp eax, 3
    setg al
    movzx eax, al
    mov dword [rbp-8], eax
    mov eax, dword [rbp-8]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
