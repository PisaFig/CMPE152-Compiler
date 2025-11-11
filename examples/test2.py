# Test Case 2: Control Flow Structures
# Demonstrates: if/elif/else statements, while loops, for loops, nested structures

print("Control Flow Test")
print("=================")

# Test 1: If/elif/else statements
score = 85

if score >= 90:
    grade = "A"
    print("Excellent!")
elif score >= 80:
    grade = "B"
    print("Good job!")
elif score >= 70:
    grade = "C"
    print("Satisfactory")
else:
    grade = "F"
    print("Needs improvement")

print("Score:", score)
print("Grade:", grade)

# Test 2: While loop
print("\nCounting down:")
counter = 5
while counter > 0:
    print("Count:", counter)
    counter = counter - 1
print("Blast off!")

# Test 3: For loop with list
print("\nIterating through numbers:")
numbers = [1, 2, 3, 4, 5]
for num in numbers:
    if num % 2 == 0:
        print(num, "is even")
    else:
        print(num, "is odd")

# Test 4: For loop with string
print("\nIterating through string:")
word = "Python"
for char in word:
    print("Character:", char)

# Test 5: Nested control structures
print("\nNested loops and conditions:")
i = 1
while i <= 3:
    print("Outer loop iteration:", i)
    j = 1
    while j <= 2:
        if i == j:
            print("  i equals j:", i)
        else:
            print("  i != j:", i, "!=", j)
        j = j + 1
    i = i + 1

# Test 6: List operations
print("\nList operations:")
my_list = [10, 20, 30]
print("Original list:", my_list)
print("First element:", my_list[0])
print("Last element:", my_list[2])

# Test 7: Complex conditions
x = 15
y = 25
if x > 10 and y > 20:
    print("Both conditions met")
    if x + y > 30:
        print("Sum is greater than 30")
    else:
        print("Sum is 30 or less")