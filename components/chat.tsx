"use client"

import { useState } from "react"
import {ChatArea} from "./chat-area"
import {ChatInput} from "./chat-input"

interface Message {
  id: number
  role: "user" | "assistant"
  content: string
  created_at: string
  attachments?: any[]
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return

    const userMsg: Message = {
      id: Date.now(),
      role: "user",
      content: message,
      created_at: new Date().toISOString(),
    }
    setMessages(prev => [...prev, userMsg])

    try {
      const res = await fetch(
        `http://localhost:8000/ask?prompt=${encodeURIComponent(message)}`
      )
      const data = await res.json()

      const assistantMsg: Message = {
        id: Date.now() + 1,
        role: "assistant",
        content: data.response,
        created_at: new Date().toISOString(),
      }

      setMessages(prev => [...prev, assistantMsg])
    } catch (error) {
      const errorMsg: Message = {
        id: Date.now() + 2,
        role: "assistant",
        content: " Erreur : Impossible de contacter le serveur.",
        created_at: new Date().toISOString(),
      }
      setMessages(prev => [...prev, errorMsg])
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gray-100">
      <ChatArea messages={messages} />
      <ChatInput onSendMessage={handleSendMessage} />
    </div>
  )
}
