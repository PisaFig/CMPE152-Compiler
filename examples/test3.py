# Test Case 3: Functions and Advanced Features
# Demonstrates: function definitions, recursion, parameter passing, return values

print("Functions and Advanced Features Test")
print("===================================")

# Test 1: Simple function with parameters
def greet(name):
    message = "Hello, " + name + "!"
    return message

# Test 2: Function with multiple parameters
def add_numbers(a, b):
    result = a + b
    return result

# Test 3: Function with local variables
def calculate_area(length, width):
    area = length * width
    perimeter = 2 * (length + width)
    print("Area:", area)
    print("Perimeter:", perimeter)
    return area

# Test 4: Recursive function
def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)

# Test 5: Function that uses control flow
def find_max(numbers):
    if len(numbers) == 0:
        return 0
    
    max_val = numbers[0]
    for num in numbers:
        if num > max_val:
            max_val = num
    return max_val

# Test 6: Function with boolean logic
def is_prime(n):
    if n <= 1:
        return False
    
    i = 2
    while i * i <= n:
        if n % i == 0:
            return False
        i = i + 1
    return True

# Main program - test all functions
print("Testing simple function:")
greeting = greet("CMPE 152 Student")
print(greeting)

print("\nTesting addition function:")
sum_result = add_numbers(15, 25)
print("15 + 25 =", sum_result)

print("\nTesting area calculation:")
rectangle_area = calculate_area(5, 8)
print("Returned area:", rectangle_area)

print("\nTesting factorial function:")
fact_5 = factorial(5)
print("5! =", fact_5)

fact_0 = factorial(0)
print("0! =", fact_0)

print("\nTesting max function:")
test_numbers = [3, 7, 2, 9, 1, 6]
maximum = find_max(test_numbers)
print("Numbers:", test_numbers)
print("Maximum:", maximum)

print("\nTesting prime function:")
test_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
for val in test_values:
    if is_prime(val):
        print(val, "is prime")
    else:
        print(val, "is not prime")

# Test 7: Function calls within expressions
print("\nFunction calls in expressions:")
double_factorial = factorial(4) * 2
print("4! * 2 =", double_factorial)

sum_of_factorials = factorial(3) + factorial(4)
print("3! + 4! =", sum_of_factorials)

# Test 8: Nested function calls
print("\nNested function calls:")
nested_result = add_numbers(factorial(3), factorial(2))
print("factorial(3) + factorial(2) =", nested_result)