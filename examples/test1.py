# Test Case 1: Basic Expressions and Variables
# Demonstrates: variable assignment, arithmetic operations, print statements

# Get user input
x = int(input("x: "))
y = float(input("y: "))
name = input("name: ")
is_valid_input = input("is_valid: ")
is_valid = is_valid_input.lower() in ['true', 't', '1', 'yes']

# Arithmetic expressions
sum_result = x + 5
diff_result = x - y
product = x * 2
quotient = x / 4
remainder = x % 3
power_result = x ** 2

# Print results
print("\nBasic Expressions Test")
print("======================")
print(f"x = {x}")
print(f"y = {y}")
print(f"Sum: {sum_result}")
print(f"Difference: {diff_result}")
print(f"Product: {product}")
print(f"Quotient: {quotient}")
print(f"Remainder: {remainder}")
print(f"Power: {power_result}")
print(f"Name: {name}")
print(f"Is valid: {is_valid}")

# String operations
greeting = "Hello, " + name
print(f"Greeting: {greeting}")

# Boolean operations
result1 = x > 5
result2 = y < 10
combined = result1 and result2
print(f"x > 5: {result1}")
print(f"y < 10: {result2}")
print(f"Both true: {combined}")