"""
Setup configuration for MiniCompiler
Позволяет установить проект как пакет и использовать команду 'compiler'
"""

from setuptools import setup, find_packages

setup(
    name="minicompiler",
    version="1.0.0",
    description="Лексический анализатор для учебного компилятора",
    author="Student",
    author_email="student@example.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Зависимости проекта
    install_requires=[
        # Нет внешних зависимостей для Sprint 1
    ],
    
    # Точки входа - создают команду в терминале
    entry_points={
        "console_scripts": [
            "compiler=src.main:main",  # команда 'compiler' запускает main()
            "compiler-test=src.main:test",  # команда 'compiler-test' запускает test()
        ],
    },
    
    # Метаданные
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)