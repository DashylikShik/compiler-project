import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Импортируем наш сканер
from src.lexer.scanner import Scanner

def test_file(filename):
    """
    Функция для тестирования одного файла
    filename - имя файла в папке examples (например, "test1.src")
    """
    file_path = os.path.join(os.path.dirname(__file__), '..', 'examples', filename)
    
    print(f"ТЕСТИРУЕМ ФАЙЛ: {filename}")
    
    # Проверяем, существует ли файл
    if not os.path.exists(file_path):
        print(f" ОШИБКА: Файл {file_path} не найден!")
        return
    
    # Читаем содержимое файла
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    
    print("\n ИСХОДНЫЙ КОД:")
    print(code)
    
    # Создаем сканер и анализируем код
    scanner = Scanner(code)
    
    print("\n ТОКЕНЫ:")
    for token in scanner.tokens:
        print(token)
    
    # Проверяем ошибки
    if scanner.errors:
        print("\n НАЙДЕНЫ ОШИБКИ:")
        for error in scanner.errors:
            print(f"  • {error}")
    else:
        print("\ОШИБОК НЕТ!")
    
    # Статистика
    print(f"\n СТАТИСТИКА:")
    print(f"   Всего токенов: {len(scanner.tokens)}")
    print(f"   Строк в коде: {scanner.line}")
    print(f"   Размер файла: {len(code)} символов")

def test_all_examples():
    """
    Функция для тестирования ВСЕХ файлов в папке examples
    """
    print("ЗАПУСК ВСЕХ ТЕСТОВ")
    
    # Путь к папке examples
    examples_dir = os.path.join(os.path.dirname(__file__), '..', 'examples')
    
    # Проверяем, существует ли папка
    if not os.path.exists(examples_dir):
        print(f" ОШИБКА: Папка {examples_dir} не найдена!")
        return
    
    # Получаем список всех .src файлов в папке examples
    src_files = [f for f in os.listdir(examples_dir) if f.endswith('.src')]
    
    if not src_files:
        print(" В папке examples нет .src файлов!")
        return
    
    print(f"\nНайдено файлов для тестирования: {len(src_files)}")
    
    # Тестируем каждый файл
    for i, filename in enumerate(src_files, 1):
        print(f"ТЕСТ {i} из {len(src_files)}")
        test_file(filename)
        
        # Ждем нажатия Enter между тестами
        if i < len(src_files):
            input("\nНажми Enter для продолжения...")

if __name__ == "__main__":
    """
    Главная функция, которая запускается при выполнении скрипта
    """
    print(" ЛЕКСИЧЕСКИЙ АНАЛИЗАТОР MiniCompiler")
    print("\nЧто хотите сделать?")
    print("1. Протестировать ВСЕ примеры")
    print("2. Протестировать конкретный файл")
    print("3. Выйти")
    
    choice = input("\nВаш выбор (1, 2 или 3): ")
    
    if choice == "1":
        test_all_examples()
    elif choice == "2":
        print("\nДоступные файлы в папке examples:")
        examples_dir = os.path.join(os.path.dirname(__file__), '..', 'examples')
        if os.path.exists(examples_dir):
            files = [f for f in os.listdir(examples_dir) if f.endswith('.src')]
            for i, f in enumerate(files, 1):
                print(f"{i}. {f}")
        
        filename = input("\nВведите имя файла (например, test1.src): ")
        test_file(filename)
    else:
        print("До свидания!")