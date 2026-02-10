"""Curriculum data for the 8-module Python learning path."""

CURRICULUM = [
    {
        "id": "mod-1",
        "name": "Python Basics",
        "order": 1,
        "topics": ["Variables", "Data Types", "Input/Output", "Operators", "Type Conversion"],
        "exercises_count": 10,
        "description": "Learn the fundamentals of Python programming including variables, data types, and basic operations.",
    },
    {
        "id": "mod-2",
        "name": "Control Flow",
        "order": 2,
        "topics": ["Conditionals (if/elif/else)", "For Loops", "While Loops", "Break & Continue", "Nested Loops"],
        "exercises_count": 12,
        "description": "Master decision-making and repetition in Python with conditionals and loops.",
    },
    {
        "id": "mod-3",
        "name": "Data Structures",
        "order": 3,
        "topics": ["Lists", "Tuples", "Dictionaries", "Sets", "List Comprehensions"],
        "exercises_count": 12,
        "description": "Work with Python's built-in data structures for organizing and manipulating data.",
    },
    {
        "id": "mod-4",
        "name": "Functions",
        "order": 4,
        "topics": ["Defining Functions", "Parameters & Arguments", "Return Values", "Scope & Lifetime", "Lambda Functions"],
        "exercises_count": 10,
        "description": "Write reusable code with functions, understand scope, and use lambda expressions.",
    },
    {
        "id": "mod-5",
        "name": "Object-Oriented Programming",
        "order": 5,
        "topics": ["Classes & Objects", "Attributes & Methods", "Inheritance", "Encapsulation", "Polymorphism"],
        "exercises_count": 10,
        "description": "Design programs using classes, inheritance, and other OOP principles.",
    },
    {
        "id": "mod-6",
        "name": "File Handling",
        "order": 6,
        "topics": ["Reading Files", "Writing Files", "CSV Processing", "JSON Processing", "Context Managers"],
        "exercises_count": 8,
        "description": "Read and write files in various formats including text, CSV, and JSON.",
    },
    {
        "id": "mod-7",
        "name": "Error Handling",
        "order": 7,
        "topics": ["Try/Except", "Exception Types", "Custom Exceptions", "Debugging Techniques", "Assertions"],
        "exercises_count": 8,
        "description": "Handle errors gracefully and debug Python programs effectively.",
    },
    {
        "id": "mod-8",
        "name": "Libraries & APIs",
        "order": 8,
        "topics": ["Installing Packages (pip)", "Working with APIs", "Virtual Environments", "Popular Libraries", "Building Projects"],
        "exercises_count": 8,
        "description": "Use external libraries, interact with APIs, and manage Python environments.",
    },
]


def get_all_modules():
    """Return all curriculum modules."""
    return CURRICULUM


def get_module(module_id: str):
    """Return a specific module by ID."""
    for module in CURRICULUM:
        if module["id"] == module_id:
            return module
    return None
