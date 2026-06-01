section .text
extern malloc
global main


main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov rdi, 12
    call malloc
    mov qword [rbp-8], rax
    mov r10, [rbp-8]
    mov r11, 0
    shl r11, 2
    add r10, r11
    mov eax, 1
    mov dword [r10], eax
    mov r10, [rbp-8]
    mov r11, 1
    shl r11, 2
    add r10, r11
    mov eax, 2
    mov dword [r10], eax
    mov r10, [rbp-8]
    mov r11, 2
    shl r11, 2
    add r10, r11
    mov eax, 3
    mov dword [r10], eax
    mov r10, [rbp-8]
    mov r11, 0
    shl r11, 2
    add r10, r11
    mov eax, dword [r10]
    mov qword [rbp-16], rax
    mov eax, dword [rbp-16]
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
