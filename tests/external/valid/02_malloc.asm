section .text
extern free
extern malloc
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov rdi, 4
    call malloc
    mov qword [rbp-8], rax
    mov eax, dword [rbp-8]
    mov dword [rbp-16], eax
    mov eax, [rbp-16]
    cmp eax, 0
    setne al
    movzx eax, al
    mov dword [rbp-24], eax
    mov eax, [rbp-24]
    cmp eax, 0
    jne L1
    jmp L2

L1:
    mov rdi, [rbp-16]
    call free
    mov qword [rbp-32], rax
    jmp L3

L2:
    jmp L3

L3:
    mov eax, 0
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
