import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'LearnFlow - AI-Powered Python Learning',
  description: 'Learn Python with AI-powered assistance and real-time code execution',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-slate-900 text-slate-200">{children}</body>
    </html>
  )
}
