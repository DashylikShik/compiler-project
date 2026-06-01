# Тестирование MiniCompiler

## 1. Единый запуск

```bash
python3 tests/all_tests.py
```

или:

```bash
make test-all
```

Единый раннер не удаляет старые тесты. Он последовательно запускает существующие раннеры проекта и выводит общий статус.

## 2. Наборы тестов

### Лексер

```bash
python3 tests/test_runner.py
```

Проверяются 20 валидных и 10 невалидных golden-тестов.

### Парсер

```bash
python3 -m pytest tests/parser -v
```

### Семантика

```bash
python3 -m unittest tests.test_semantic -v
```

### IR

```bash
python3 tests/ir/test_runner.py
python3 tests/ir/test_golden.py
```

### Codegen

```bash
python3 tests/codegen/test_runner.py
```

### Control Flow

```bash
python3 tests/control_flow/test_runner.py
python3 tests/control_flow/test_golden.py
```

### Оптимизации

```bash
python3 -m unittest tests.optimization.test_constant_folding -v
```

### Sprint 7 integration

```bash
python3 run_valid_tests.py
```

## 3. Проверка invalid-тестов Sprint 7

```bash
python3 src/main.py check tests/array/invalid/01_out_of_bounds.src
python3 src/main.py check tests/external/invalid/01_wrong_args.src
```

Оба теста должны завершаться с ошибками семантического анализа.

## 4. Golden testing

Golden-тест сравнивает фактический вывод с заранее сохранённым expected-файлом.

Если логика вывода ошибок осознанно изменилась, expected-файл нужно обновить. Например, если лексер теперь группирует `123.456.789` как одну ошибку `Неправильный формат числа`, expected должен соответствовать новой логике.

## 5. Отчёты

`tests/all_tests.py` создаёт каталог:

```text
tests/final_reports/
```

В нём сохраняется JSON-отчёт с результатами последнего запуска.
