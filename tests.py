from functions.write_file import write_file

def run_tests():
    print("Test 1: Write to lorem.txt in root")
    print(write_file("calculator", "lorem.txt", "wait, this isn't lorem ipsum"))
    print("\n" + "="*50 + "\n")

    print("Test 2: Write to pkg/morelorem.txt")
    print(write_file("calculator", "pkg/morelorem.txt", "lorem ipsum dolor sit amet"))
    print("\n" + "="*50 + "\n")

    print("Test 3: Attempt to write to /tmp/temp.txt (should fail)")
    print(write_file("calculator", "/tmp/temp.txt", "this should not be allowed"))
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    run_tests()
