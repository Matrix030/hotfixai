from functions.get_function_content import get_file_content

def run_tests():
    print("Test 1: main.py")
    print(get_file_content("calculator", "main.py"))  # Preview first 300 chars
    print("\n" + "="*50 + "\n")

    print("Test 2: pkg/calculator.py")
    print(get_file_content("calculator", "pkg/calculator.py"))
    print("\n" + "="*50 + "\n")

    print("Test 3: outside dir (/bin/cat)")
    print(get_file_content("calculator", "/bin/cat"))
    print("\n" + "="*50 + "\n")

    print("Test 4: non-existent file")
    print(get_file_content("calculator", "pkg/does_not_exist.py"))
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    run_tests()
