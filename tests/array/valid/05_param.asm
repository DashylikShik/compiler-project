section .text
extern malloc
global main


sum:
    push rbp
    mov rbp, rsp
    sub rsp, 64
    mov [rbp-8], rsi
    mov [rbp-16], 0
    mov [rbp-24], 0
    jmp L1

L1:
    mov eax, [rbp-24]
    cmp eax, [rbp-8]
    setl al
    movzx eax, al
    mov [rbp-32], eax
    cmp [rbp-32], 0
    jne L2
    jmp L4

L2:
    mov r10, rdi
    movsxd r11, dword [rbp-24]
    shl r11, 2
    add r10, r11
    mov eax, dword [r10]
    mov [rbp-40], rax
    mov eax, [rbp-16]
    add eax, [rbp-40]
    mov [rbp-48], eax
    mov eax, [rbp-48]
    mov [rbp-16], eax
    jmp L3

L3:
    mov eax, [rbp-24]
    add eax, 1
    mov [rbp-56], eax
    mov eax, [rbp-56]
    mov [rbp-24], eax
    jmp L1

L4:
    mov eax, dword [rbp-16]
    mov rsp, rbp
    pop rbp
    ret

main:
    push rbp
    mov rbp, rsp
    sub rsp, 32
    mov rdi, 20
    call malloc
    mov [rbp-8], rax
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
    mov r11, 3
    shl r11, 2
    add r10, r11
    mov eax, 4
    mov dword [r10], eax
    mov r10, [rbp-8]
    mov r11, 4
    shl r11, 2
    add r10, r11
    mov eax, 5
    mov dword [r10], eax
    mov rdi, [rbp-8]
    mov rsi, 5
    call sum
    mov [rbp-16], rax
    mov eax, 15
    mov rsp, rbp
    pop rbp
    ret

exit:
    mov rax, 60
    syscall
