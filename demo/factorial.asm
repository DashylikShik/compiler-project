section .text
global main


factorial:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov [rbp-8], n
    cmp [rbp-16], 0
    jne L1
    jmp L2

L1:
    mov rax, 1
    mov rsp, rbp
    pop rbp
    ret

L2:
    mov eax, [rbp-8]
    sub eax, 1
    mov [rbp-24], eax
    mov edi, [rbp-24]
    call factorial
    mov [rbp-32], eax
    mov eax, [rbp-8]
    imul eax, [rbp-32]
    mov [rbp-40], eax
    mov rax, [rbp-40]
    mov rsp, rbp
    pop rbp
    ret

main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov edi, 5
    call factorial
    mov [rbp-8], eax
    mov rax, [rbp-8]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
