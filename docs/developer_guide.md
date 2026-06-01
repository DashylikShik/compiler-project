# Руководство разработчика MiniCompiler

## 1. Архитектура

Компилятор разделён на этапы:

```text
source.src
   ↓
lexer.Scanner
   ↓
parser.Parser
   ↓
semantic.SemanticAnalyzer
   ↓
ir.IRGenerator
   ↓
ir.optimizer.OptimizationPipeline
   ↓
codegen.X86Generator
   ↓
program.asm
   ↓
nasm + gcc
   ↓
executable
```

## 2. Модули

### `src/lexer`

- `scanner.py` — разбивает исходный текст на токены;
- `token.py` — типы токенов и формат печати.

Тесты:

```bash
python3 tests/test_runner.py
```

### `src/parser`

- `parser.py` — рекурсивный нисходящий парсер;
- `ast.py` — классы узлов AST;
- `grammar.txt` — грамматика.

Тесты:

```bash
python3 -m pytest tests/parser -v
```

### `src/semantic`

- `analyzer.py` — семантический анализ;
- `symbol_table.py` — области видимости и символы;
- `type_system.py` — типы и совместимость;
- `errors.py` — формат ошибок.

Тесты:

```bash
python3 -m unittest tests.test_semantic -v
```

### `src/ir`

- `ir_instructions.py` — инструкции IR;
- `ir_generator.py` — генерация IR;
- `ir_printer.py` — печать IR;
- `basic_block.py` — базовые блоки и CFG;
- `optimizer/` — оптимизации.

Тесты:

```bash
python3 tests/ir/test_runner.py
python3 tests/ir/test_golden.py
```

### `src/codegen`

- `x86_generator.py` — генерация NASM x86-64 assembly.

Тесты:

```bash
python3 tests/codegen/test_runner.py
```

## 3. Как добавить новый синтаксис

1. Добавить токены в `src/lexer/token.py`.
2. Научить `Scanner` распознавать новый токен.
3. Добавить AST-узел в `src/parser/ast.py`.
4. Добавить правило в `src/parser/parser.py`.
5. Добавить семантическую проверку в `SemanticAnalyzer`.
6. Добавить генерацию IR в `IRGenerator`.
7. Добавить генерацию x86 в `X86Generator`.
8. Добавить тесты во все нужные уровни.

## 4. Как добавить оптимизацию

1. Создать класс оптимизации в `src/ir/optimizer/`.
2. Реализовать метод `optimize(program)`.
3. Подключить оптимизацию в `OptimizationPipeline`.
4. Добавить статистику в `get_stats()`.
5. Добавить unit-тест и integration-тест.

## 5. Диагностика

Полезные команды:

```bash
python3 src/main.py lex file.src
python3 src/main.py parse --format text file.src
python3 src/main.py check --symbols file.src
python3 src/main.py ir --verbose file.src
python3 src/main.py compile file.src --verbose
python3 src/main.py compile file.src --optimize --verbose
```

## 6. Частые проблемы

### `dot` не найден

Установить Graphviz:

```bash
sudo apt install graphviz
```

### `nasm` не найден

```bash
sudo apt install nasm
```

### `pow` или `sqrt` не линкуются

Нужно добавить `-lm`:

```bash
gcc -no-pie program.o -lm -o program
```

или использовать:

```bash
python3 mycc.py program.src -lm -o program
```
