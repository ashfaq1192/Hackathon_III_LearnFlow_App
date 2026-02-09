'use client'

import { useState, useEffect } from 'react'

interface Exercise {
  id: string
  title: string
  description: string
  difficulty: string
  starter_code?: string
  expected_output?: string
  hints?: string[]
}

interface ExercisePanelProps {
  onSelectExercise?: (exercise: Exercise) => void
}

const DEFAULT_EXERCISES: Exercise[] = [
  // Easy exercises
  {
    id: '1',
    title: 'Hello World',
    description: 'Print "Hello, World!" to the console.',
    difficulty: 'Easy',
    starter_code: '# Print Hello, World!\n',
    expected_output: 'Hello, World!',
    hints: ['Use the print() function'],
  },
  {
    id: '2',
    title: 'Variables',
    description: 'Create a variable called "name" with your name and print a greeting.',
    difficulty: 'Easy',
    starter_code: '# Create a variable and print a greeting\nname = ""\nprint(f"Hello, {name}!")\n',
    expected_output: 'Hello, <your name>!',
    hints: ['Assign a string to the name variable'],
  },
  {
    id: '3',
    title: 'Basic Math',
    description: 'Calculate and print the sum, difference, product, and quotient of 10 and 3.',
    difficulty: 'Easy',
    starter_code: '# Calculate basic math operations with 10 and 3\na = 10\nb = 3\n\n# Print sum, difference, product, quotient\n',
    expected_output: '13\n7\n30\n3.333...',
    hints: ['Use +, -, *, / operators', 'Division returns a float'],
  },
  {
    id: '4',
    title: 'String Concatenation',
    description: 'Combine first_name and last_name into a full name and print it.',
    difficulty: 'Easy',
    starter_code: '# Combine first and last name\nfirst_name = "John"\nlast_name = "Doe"\n\n# Create and print full_name\n',
    expected_output: 'John Doe',
    hints: ['Use + to concatenate strings', 'Add a space between names'],
  },
  // Medium exercises
  {
    id: '5',
    title: 'Loop Practice',
    description: 'Write a for loop that prints numbers 1 to 10.',
    difficulty: 'Medium',
    starter_code: '# Print numbers 1 to 10 using a for loop\n',
    expected_output: '1\n2\n3\n...\n10',
    hints: ['Use range(1, 11)', 'Remember range() is exclusive of the end'],
  },
  {
    id: '6',
    title: 'List Operations',
    description: 'Create a list of 5 fruits and print each one using a loop.',
    difficulty: 'Medium',
    starter_code: '# Create a list of fruits and print each one\nfruits = []\n',
    expected_output: 'apple\nbanana\n...',
    hints: ['Use a for loop to iterate over the list'],
  },
  {
    id: '7',
    title: 'Function Definition',
    description: 'Write a function called "is_even" that returns True if a number is even.',
    difficulty: 'Medium',
    starter_code: '# Define the is_even function\ndef is_even(n):\n    pass\n\n# Test it\nprint(is_even(4))  # True\nprint(is_even(7))  # False\n',
    expected_output: 'True\nFalse',
    hints: ['Use the modulo operator %', 'n % 2 == 0 means even'],
  },
  {
    id: '8',
    title: 'Dictionary Basics',
    description: 'Create a dictionary with person info (name, age, city) and print each key-value pair.',
    difficulty: 'Medium',
    starter_code: '# Create a person dictionary\nperson = {}\n\n# Print each key-value pair\n',
    expected_output: 'name: John\nage: 25\ncity: NYC',
    hints: ['Use curly braces {} for dictionaries', 'Use .items() to iterate'],
  },
  {
    id: '9',
    title: 'List Comprehension',
    description: 'Create a list of squares for numbers 1-10 using list comprehension.',
    difficulty: 'Medium',
    starter_code: '# Create squares using list comprehension\nsquares = []\n\nprint(squares)\n',
    expected_output: '[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]',
    hints: ['Syntax: [expression for item in iterable]', 'Use x**2 for square'],
  },
  // Hard exercises
  {
    id: '10',
    title: 'FizzBuzz',
    description: 'Print 1-20. For multiples of 3 print "Fizz", multiples of 5 print "Buzz", both print "FizzBuzz".',
    difficulty: 'Hard',
    starter_code: '# FizzBuzz challenge\nfor i in range(1, 21):\n    # Your code here\n    pass\n',
    expected_output: '1\n2\nFizz\n4\nBuzz\n...',
    hints: ['Check divisibility by 15 first (both 3 and 5)', 'Use elif for multiple conditions'],
  },
  {
    id: '11',
    title: 'Palindrome Checker',
    description: 'Write a function that checks if a string is a palindrome (reads same forwards and backwards).',
    difficulty: 'Hard',
    starter_code: '# Check if a string is a palindrome\ndef is_palindrome(s):\n    pass\n\n# Test cases\nprint(is_palindrome("radar"))  # True\nprint(is_palindrome("hello"))  # False\nprint(is_palindrome("level"))  # True\n',
    expected_output: 'True\nFalse\nTrue',
    hints: ['Compare string with its reverse', 'Use slicing [::-1] to reverse'],
  },
  {
    id: '12',
    title: 'Prime Numbers',
    description: 'Write a function that returns all prime numbers up to n.',
    difficulty: 'Hard',
    starter_code: '# Find all prime numbers up to n\ndef get_primes(n):\n    primes = []\n    # Your code here\n    return primes\n\nprint(get_primes(20))\n',
    expected_output: '[2, 3, 5, 7, 11, 13, 17, 19]',
    hints: ['A prime is only divisible by 1 and itself', 'Check divisibility up to sqrt(n)'],
  },
  {
    id: '13',
    title: 'Fibonacci Sequence',
    description: 'Write a function that returns the first n Fibonacci numbers.',
    difficulty: 'Hard',
    starter_code: '# Generate Fibonacci sequence\ndef fibonacci(n):\n    # Your code here\n    pass\n\nprint(fibonacci(10))\n',
    expected_output: '[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]',
    hints: ['Each number is sum of previous two', 'Start with [0, 1]'],
  },
  {
    id: '14',
    title: 'Word Frequency Counter',
    description: 'Count the frequency of each word in a sentence and return as a dictionary.',
    difficulty: 'Hard',
    starter_code: '# Count word frequencies\ndef word_frequency(sentence):\n    # Your code here\n    pass\n\ntext = "the quick brown fox jumps over the lazy dog the fox"\nprint(word_frequency(text))\n',
    expected_output: "{'the': 3, 'quick': 1, 'brown': 1, ...}",
    hints: ['Use split() to get words', 'Use a dictionary to count'],
  },
]

export default function ExercisePanel({ onSelectExercise }: ExercisePanelProps) {
  const [exercises, setExercises] = useState<Exercise[]>(DEFAULT_EXERCISES)
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const fetchExercises = async () => {
      setLoading(true)
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || ''
        const res = await fetch(`${apiUrl}/api/exercises`)
        if (res.ok) {
          const data = await res.json()
          if (data.length > 0) {
            setExercises(data)
          }
        }
      } catch {
        // Fall back to default exercises
      }
      setLoading(false)
    }
    fetchExercises()
  }, [])

  const handleSelect = (exercise: Exercise) => {
    setSelectedExercise(exercise)
    onSelectExercise?.(exercise)
  }

  const difficultyColor = (d: string) => {
    if (d === 'Easy') return 'bg-green-900/50 text-green-400 border border-green-800'
    if (d === 'Medium') return 'bg-yellow-900/50 text-yellow-400 border border-yellow-800'
    return 'bg-red-900/50 text-red-400 border border-red-800'
  }

  return (
    <div className="p-3">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3 px-1">
        Exercises
      </h2>

      {loading && (
        <p className="text-slate-500 text-xs mb-2 px-1">Loading...</p>
      )}

      <div className="space-y-1">
        {exercises.map((exercise) => (
          <div
            key={exercise.id}
            onClick={() => handleSelect(exercise)}
            className={`p-2.5 rounded cursor-pointer transition-colors ${
              selectedExercise?.id === exercise.id
                ? 'bg-blue-900/30 border-l-2 border-l-blue-500 pl-2'
                : 'hover:bg-slate-700/50 border-l-2 border-l-transparent pl-2'
            }`}
          >
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-medium text-slate-200">{exercise.title}</h3>
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${difficultyColor(exercise.difficulty)}`}>
                {exercise.difficulty}
              </span>
            </div>
          </div>
        ))}
      </div>

      {selectedExercise && (
        <div className="mt-3 p-3 bg-slate-900/50 border border-slate-700 rounded">
          <h3 className="text-sm font-semibold text-slate-200">{selectedExercise.title}</h3>
          <p className="text-xs text-slate-400 mt-1.5">{selectedExercise.description}</p>
          {selectedExercise.hints && selectedExercise.hints.length > 0 && (
            <div className="mt-2">
              <p className="text-[10px] font-medium text-slate-500 uppercase">Hints</p>
              <ul className="text-xs text-slate-400 list-disc list-inside mt-1 space-y-0.5">
                {selectedExercise.hints.map((hint, i) => (
                  <li key={i}>{hint}</li>
                ))}
              </ul>
            </div>
          )}
          {selectedExercise.expected_output && (
            <div className="mt-2">
              <p className="text-[10px] font-medium text-slate-500 uppercase">Expected Output</p>
              <code className="text-xs text-green-400">{selectedExercise.expected_output}</code>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
