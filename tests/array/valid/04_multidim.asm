section .text
extern malloc
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 64
    mov rdi, 48
    call malloc
    mov qword [rbp-8], rax
    mov eax, 1
    imul eax, 4
    mov dword [rbp-16], eax
    mov eax, [rbp-16]
    add eax, 2
    mov dword [rbp-24], eax
    mov r10, [rbp-8]
    movsxd r11, dword [rbp-24]
    shl r11, 2
    add r10, r11
    mov eax, 42
    mov dword [r10], eax
    mov eax, 1
    imul eax, 4
    mov dword [rbp-32], eax
    mov eax, [rbp-32]
    add eax, 2
    mov dword [rbp-40], eax
    mov r10, [rbp-8]
    movsxd r11, dword [rbp-40]
    shl r11, 2
    add r10, r11
    mov eax, dword [r10]
    mov qword [rbp-48], rax
    mov eax, dword [rbp-48]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
