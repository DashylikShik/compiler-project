section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov eax, 1
    cmp eax, 2
    setg al
    movzx eax, al
    mov [rbp-8], eax
    mov eax, [rbp-8]
    cmp eax, 0
    jne L1
    jmp L2

L1:
    mov eax, 10
    mov rsp, rbp
    pop rbp
    ret

L2:
    jmp L3

L3:
    mov eax, 5
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
