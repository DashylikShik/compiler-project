import os

def create_test_files():
    """Создает все необходимые тестовые файлы"""
    
    base_dir = os.path.dirname(os.path.dirname(__file__))
    valid_dir = os.path.join(base_dir, 'parser', 'valid')
    invalid_dir = os.path.join(base_dir, 'parser', 'invalid')
    
    
    # expressions/test_arith.src
    with open(os.path.join(valid_dir, 'expressions', 'test_arith.src'), 'w') as f:
        f.write("""
1 + 2 * 3;
(4 + 5) * 6;
-7 + 8;
""".strip())
    
    # expressions/test_compare.src
    with open(os.path.join(valid_dir, 'expressions', 'test_compare.src'), 'w') as f:
        f.write("""
x > y;
a <= b;
c == d;
e != f;
""".strip())
    
    # expressions/test_logical.src
    with open(os.path.join(valid_dir, 'expressions', 'test_logical.src'), 'w') as f:
        f.write("""
x && y;
a || b;
!flag;
(x > 0) && (y < 10);
""".strip())
    
    # statements/test_var_decl.src
    with open(os.path.join(valid_dir, 'statements', 'test_var_decl.src'), 'w') as f:
        f.write("""
int x;
float y = 3.14;
bool flag = true;
int a = 5;
""".strip())
    
    # statements/test_if.src
    with open(os.path.join(valid_dir, 'statements', 'test_if.src'), 'w') as f:
        f.write("""
if (x > 0) {
    return x;
} else {
    return -x;
}
""".strip())
    
    # statements/test_while.src
    with open(os.path.join(valid_dir, 'statements', 'test_while.src'), 'w') as f:
        f.write("""
while (i < 10) {
    i = i + 1;
}
""".strip())
    
    # statements/test_for.src
    with open(os.path.join(valid_dir, 'statements', 'test_for.src'), 'w') as f:
        f.write("""
for (int i = 0; i < 10; i = i + 1) {
    print(i);
}
""".strip())
    
    # statements/test_return.src
    with open(os.path.join(valid_dir, 'statements', 'test_return.src'), 'w') as f:
        f.write("""
fn main() {
    return 0;
}
""".strip())
    
    # declarations/test_function.src
    with open(os.path.join(valid_dir, 'declarations', 'test_function.src'), 'w') as f:
        f.write("""
fn add(int a, int b) int {
    return a + b;
}
""".strip())
    
    # declarations/test_struct.src
    with open(os.path.join(valid_dir, 'declarations', 'test_struct.src'), 'w') as f:
        f.write("""
struct Point {
    int x;
    int y;
}
""".strip())
    
    # full_programs/test_factorial.src
    with open(os.path.join(valid_dir, 'full_programs', 'test_factorial.src'), 'w') as f:
        f.write("""
fn factorial(int n) int {
    int result = 1;
    while (n > 0) {
        result = result * n;
        n = n - 1;
    }
    return result;
}

fn main() {
    int x = 5;
    int f = factorial(x);
    return f;
}
""".strip())
    
    
    # syntax_errors/test_missing_paren.src
    with open(os.path.join(invalid_dir, 'syntax_errors', 'test_missing_paren.src'), 'w') as f:
        f.write("""
if (x > 0 {
    return x;
}
""".strip())
    
    # syntax_errors/test_missing_semicolon.src
    with open(os.path.join(invalid_dir, 'syntax_errors', 'test_missing_semicolon.src'), 'w') as f:
        f.write("""
int x = 5
int y = 10;
""".strip())
    
    print(" Все тестовые файлы созданы!")

if __name__ == "__main__":
    create_test_files()
    