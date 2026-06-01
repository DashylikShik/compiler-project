section .text
extern sqrt
extern pow
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 48
    mov rdi, 2
    mov rsi, 3
    call pow
    mov qword [rbp-8], rax
    mov eax, dword [rbp-8]
    mov dword [rbp-16], eax
    mov rdi, 16
    call sqrt
    mov qword [rbp-24], rax
    mov eax, dword [rbp-24]
    mov dword [rbp-32], eax
    mov eax, 0
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
