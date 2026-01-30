'use client'

import { useState, useEffect } from 'react'

interface Exercise {
  id: string
  title: string
  description: string
  difficulty: string
}

export default function ExercisePanel() {
  const [exercises, setExercises] = useState<Exercise[]>([
    {
      id: '1',
      title: 'Hello World',
      description: 'Print "Hello, World!" to the console.',
      difficulty: 'Easy',
    },
    {
      id: '2',
      title: 'Variables',
      description: 'Create a variable called "name" and print a greeting.',
      difficulty: 'Easy',
    },
    {
      id: '3',
      title: 'Loop Practice',
      description: 'Write a for loop that prints numbers 1 to 10.',
      difficulty: 'Medium',
    },
  ])
  const [selectedExercise, setSelectedExercise] = useState<Exercise | null>(null)

  return (
    <div className="bg-white rounded-lg shadow-lg p-4">
      <h2 className="text-xl font-semibold mb-4">Exercises</h2>

      <div className="space-y-3">
        {exercises.map((exercise) => (
          <div
            key={exercise.id}
            onClick={() => setSelectedExercise(exercise)}
            className={`p-3 border rounded cursor-pointer hover:bg-gray-50 transition ${
              selectedExercise?.id === exercise.id ? 'border-blue-500 bg-blue-50' : ''
            }`}
          >
            <div className="flex justify-between items-center">
              <h3 className="font-medium">{exercise.title}</h3>
              <span
                className={`text-xs px-2 py-1 rounded ${
                  exercise.difficulty === 'Easy'
                    ? 'bg-green-100 text-green-800'
                    : exercise.difficulty === 'Medium'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}
              >
                {exercise.difficulty}
              </span>
            </div>
          </div>
        ))}
      </div>

      {selectedExercise && (
        <div className="mt-4 p-4 bg-gray-50 rounded">
          <h3 className="font-semibold">{selectedExercise.title}</h3>
          <p className="text-gray-600 mt-2">{selectedExercise.description}</p>
        </div>
      )}
    </div>
  )
}
