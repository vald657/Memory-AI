"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { ChatSidebar } from "@/components/chat-sidebar"
import { ChatArea } from "@/components/chat-area"
import { ChatInput } from "@/components/chat-input"
import { Button } from "@/components/ui/button"
import { Menu } from "lucide-react"

interface Message {
  id: number
  role: "user" | "assistant"
  content: string
  created_at: string
}

interface Conversation {
  id: number
  title: string
  created_at: string
  updated_at: string
}

export default function Home() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [user, setUser] = useState<any>(null)
  const pollingInterval = useRef<NodeJS.Timeout | null>(null)

  // Vérifier l'authentification
  useEffect(() => {
    fetch("/api/auth/me")
      .then((res) => res.json())
      .then((data) => {
        if (!data.user) {
          router.push("/login")
        } else {
          setUser(data.user)
        }
      })
  }, [router])

  // Charger les conversations
  useEffect(() => {
    if (user) {
      loadConversations()
    }
  }, [user])

  // Polling pour les nouveaux messages
  useEffect(() => {
    if (currentConversationId) {
      loadMessages(currentConversationId)

      // Actualiser les messages toutes les 3 secondes
      pollingInterval.current = setInterval(() => {
        loadMessages(currentConversationId)
      }, 3000)

      return () => {
        if (pollingInterval.current) {
          clearInterval(pollingInterval.current)
        }
      }
    }
  }, [currentConversationId])

  const loadConversations = async () => {
    try {
      const res = await fetch("/api/conversations")
      const data = await res.json()
      if (res.ok) {
        setConversations(data.conversations)
      }
    } catch (error) {
      console.error("[v0] Error loading conversations:", error)
    }
  }

  const loadMessages = async (conversationId: number) => {
    try {
      const res = await fetch(`/api/conversations/${conversationId}/messages`)
      const data = await res.json()
      if (res.ok) {
        setMessages(data.messages)
      }
    } catch (error) {
      console.error("[v0] Error loading messages:", error)
    }
  }

  const handleNewChat = async () => {
    try {
      const res = await fetch("/api/conversations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: "Nouvelle conversation" }),
      })
      const data = await res.json()
      if (res.ok) {
        setCurrentConversationId(data.conversation.id)
        setMessages([])
        loadConversations()
      }
    } catch (error) {
      console.error("[v0] Error creating conversation:", error)
    }
  }

  const handleSelectConversation = (conversationId: number) => {
    setCurrentConversationId(conversationId)
  }

  const handleSendMessage = async (content: string, attachments?: any[]) => {
    if (!currentConversationId) {
      // Créer une nouvelle conversation si aucune n'est sélectionnée
      const res = await fetch("/api/conversations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: content.substring(0, 50) }),
      })
      const data = await res.json()
      if (res.ok) {
        setCurrentConversationId(data.conversation.id)
        await sendMessageToConversation(data.conversation.id, content, attachments)
        loadConversations()
      }
    } else {
      await sendMessageToConversation(currentConversationId, content, attachments)
    }
  }

  const sendMessageToConversation = async (conversationId: number, content: string, attachments?: any[]) => {
    try {
      const res = await fetch(`/api/conversations/${conversationId}/messages`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ role: "user", content, attachments }),
      })
      const data = await res.json()
      if (res.ok) {
        loadMessages(conversationId)
      }
    } catch (error) {
      console.error("[v0] Error sending message:", error)
    }
  }

  if (!user) {
    return null
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <ChatSidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        conversations={conversations}
        currentConversationId={currentConversationId}
        onNewChat={handleNewChat}
        onSelectConversation={handleSelectConversation}
      />

      <div className="flex flex-1 flex-col">
        <header className="flex items-center border-b border-border bg-background p-4 lg:hidden">
          <Button variant="ghost" size="icon" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
            <Menu className="h-5 w-5" />
          </Button>
        </header>

        <div className="flex-1 overflow-hidden">
          <ChatArea messages={messages} />
        </div>

        <ChatInput onSendMessage={handleSendMessage} />
      </div>
    </div>
  )
}
