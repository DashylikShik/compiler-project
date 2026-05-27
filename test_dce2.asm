section .text
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov [rbp-8], 5
    mov eax, 1
    cmp eax, 2
    setg al
    movzx eax, al
    mov [rbp-16], eax
    cmp [rbp-16], 0
    jne L1
    jmp L2

L1:
    mov rax, 10
    mov rsp, rbp
    pop rbp
    ret

L2:
    mov rax, 20
    mov rsp, rbp
    pop rbp
    ret

L3:
    mov [rbp-8], 100
    mov rax, [rbp-8]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
