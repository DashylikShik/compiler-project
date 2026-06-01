from setuptools import setup, find_packages

setup(
    name="minicompiler",
    version="1.0.0",
    description="Учебный компилятор MiniCompiler: lexer, parser, semantic, IR, x86 codegen, optimization",
    author="DashylikShik",
    packages=find_packages(where="src"),
    py_modules=["main"],
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "pytest",
    ],
    entry_points={
        "console_scripts": [
            "compiler=main:main",
            "mycc=main:main",
        ],
    },
    include_package_data=True,
)