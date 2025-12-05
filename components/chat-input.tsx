"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { ArrowUp, Paperclip, X } from "lucide-react"

interface ChatInputProps {
  onSendMessage?: (message: string, attachments?: any[], role?: "user" | "assistant") => void
}

export function ChatInput({ onSendMessage }: ChatInputProps) {
  const [message, setMessage] = useState("")
  const [attachments, setAttachments] = useState<any[]>([])
  const [isSending, setIsSending] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleSubmit = async () => {
    if (!message.trim()) return

    setIsSending(true)

    try {
      // 1️Ajouter le message utilisateur au parent
      onSendMessage?.(message, attachments.length > 0 ? attachments : undefined, "user")

      // Réinitialiser l'input
      setMessage("")
      setAttachments([])
    } catch (error) {
      console.error("Erreur envoi message:", error)
    } finally {
      setIsSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (!files) return

    for (const file of Array.from(files)) {
      const formData = new FormData() 
      formData.append("file", file)

      try {
        const res = await fetch("/api/upload", {
          method: "POST",
          body: formData,
        })
        const data = await res.json()
        if (res.ok) {
          setAttachments((prev) => [...prev, data.file])
        } else {
          alert(data.error || "Erreur lors de l'upload")
        }
      } catch (error) {
        console.error("Upload error:", error)
        alert("Erreur lors de l'upload du fichier")
      }
    }
  }

  const handleRemoveFile = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="border-t border-border bg-background p-4">
      <div className="mx-auto max-w-3xl">
        {attachments.length > 0 && (
          <div className="mb-2 flex flex-wrap gap-2">
            {attachments.map((file, index) => (
              <div key={index} className="flex items-center gap-2 rounded bg-muted px-3 py-2 text-sm">
                <Paperclip className="h-3 w-3" />
                <span>{file.name}</span>
                <button
                  onClick={() => handleRemoveFile(index)}
                  className="ml-1 rounded-full p-0.5 hover:bg-background"
                  type="button"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        )}
        <div className="relative flex items-end gap-2 rounded-lg border border-border bg-muted p-3">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isSending ? "IA répond..." : "Envoyer un message"}
            className="min-h-[60px] resize-none border-0 bg-transparent p-0 focus-visible:ring-0 focus-visible:ring-offset-0"
            rows={1}
            disabled={isSending}
          />
          <div className="flex items-center gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx"
              multiple
              className="hidden"
              onChange={handleFileUpload}
              disabled={isSending}
            />
            <Button size="icon" variant="ghost" onClick={() => fileInputRef.current?.click()} className="h-9 w-9" disabled={isSending}>
              <Paperclip className="h-4 w-4" />
            </Button>
            <Button size="icon" onClick={handleSubmit} disabled={!message.trim() || isSending} className="h-9 w-9 rounded-full">
              <ArrowUp className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
