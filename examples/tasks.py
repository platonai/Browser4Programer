"""
Example tasks for the Self-Evolving Programming System

These examples demonstrate various types of programming tasks
that the system can handle.
"""

# Simple examples
SIMPLE_TASKS = [
    "Write a function to check if a number is prime",
    "Create a function to reverse a string without using built-in reverse",
    "Write a function to find the largest element in a list",
]

# Intermediate examples
INTERMEDIATE_TASKS = [
    "Write a function that calculates the factorial of a number using recursion. Include proper error handling for negative numbers.",
    "Create a class to implement a basic stack data structure with push, pop, and peek operations",
    "Write a function to sort a list using bubble sort algorithm",
]

# Complex examples
COMPLEX_TASKS = [
    "Implement a simple calculator that can handle addition, subtraction, multiplication, and division with proper error handling for division by zero",
    "Create a function to validate email addresses using regular expressions",
    "Write a program that reads a text file, counts word frequencies, and prints the top 5 most common words",
]

# All examples
ALL_EXAMPLES = SIMPLE_TASKS + INTERMEDIATE_TASKS + COMPLEX_TASKS


def get_example(index: int = 0) -> str:
    """Get an example task by index"""
    if 0 <= index < len(ALL_EXAMPLES):
        return ALL_EXAMPLES[index]
    return ALL_EXAMPLES[0]


def list_examples():
    """Print all available examples"""
    print("Available example tasks:\n")
    for i, task in enumerate(ALL_EXAMPLES, 1):
        print(f"{i}. {task}")


if __name__ == "__main__":
    list_examples()
