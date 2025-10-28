"use client"

import { useEffect, useRef } from "react"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { cn } from "@/lib/utils"
import { Paperclip } from "lucide-react"

interface Message {
  id: number
  role: "user" | "assistant"
  content: string
  created_at: string
  attachments?: any[]
}

interface ChatAreaProps {
  messages?: Message[]
}

export function ChatArea({ messages = [] }: ChatAreaProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  if (messages.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center">
        <div className="flex h-20 w-20 items-center justify-center rounded-lg bg-foreground text-background">
          <span className="text-4xl font-bold">M</span>
        </div>
        <p className="mt-4 text-muted-foreground">Commencez une nouvelle conversation</p>
      </div>
    )
  }

  return (
    <ScrollArea className="h-full" ref={scrollRef}>
      <div className="mx-auto max-w-3xl space-y-6 p-6">
        {messages.map((message) => (
          <div key={message.id} className={cn("flex gap-4", message.role === "user" ? "justify-end" : "justify-start")}>
            {message.role === "assistant" && (
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-muted text-xs">AI</AvatarFallback>
              </Avatar>
            )}
            <div
              className={cn(
                "max-w-[80%] rounded-lg p-4",
                message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-foreground",
              )}
            >
              {message.attachments && message.attachments.length > 0 && (
                <div className="mb-2 flex flex-wrap gap-2">
                  {message.attachments.map((file: any, index: number) => (
                    <div
                      key={index}
                      className={cn(
                        "flex items-center gap-1 rounded px-2 py-1 text-xs",
                        message.role === "user" ? "bg-primary-foreground/20" : "bg-background",
                      )}
                    >
                      <Paperclip className="h-3 w-3" />
                      <span>{file.name}</span>
                    </div>
                  ))}
                </div>
              )}
              <p className="text-sm leading-relaxed">{message.content}</p>
            </div>
            {message.role === "user" && (
              <Avatar className="h-8 w-8">
                <AvatarFallback className="bg-primary text-primary-foreground text-xs">U</AvatarFallback>
              </Avatar>
            )}
          </div>
        ))}
      </div>
    </ScrollArea>
  )
}
