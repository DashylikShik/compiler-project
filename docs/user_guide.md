# Руководство пользователя MiniCompiler

## 1. Установка

Для WSL Ubuntu:

```bash
sudo apt update
sudo apt install python3 python3-pip nasm gcc make graphviz
python3 -m pip install pytest
```

## 2. Проверка проекта

```bash
make test-all
```

или:

```bash
python3 tests/all_tests.py
```

## 3. Компиляция программы

Файл `hello.src`:

```c
extern int printf(char* format, ...);

fn main() -> int {
    printf("Hello from MiniCompiler!\n");
    return 0;
}
```

Компиляция через старый интерфейс:

```bash
python3 src/main.py compile hello.src
nasm -f elf64 hello.asm -o hello.o
gcc -no-pie hello.o -o hello
./hello
```

Компиляция через CLI Sprint 8:

```bash
python3 mycc.py hello.src -o hello
./hello
```

## 4. Получить ассемблер

```bash
python3 mycc.py -S hello.src -o hello.asm
```

## 5. Получить объектный файл

```bash
python3 mycc.py -c hello.src -o hello.o
```

## 6. Оптимизация

```bash
python3 mycc.py -O2 demo/optimization_demo.src -o optimization_demo
./optimization_demo
echo $?
```

## 7. AST и IR

```bash
python3 mycc.py --ast examples/test3.src
python3 mycc.py --ir demo/optimization_demo.src
```

## 8. Demo

```bash
make demo
```

или:

```bash
bash demo/run_demo.sh
```

## 9. Проверка ошибок

```bash
python3 src/main.py check tests/array/invalid/01_out_of_bounds.src
python3 src/main.py check tests/external/invalid/01_wrong_args.src
```

Ожидается, что эти программы не пройдут семантический анализ.
