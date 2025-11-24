"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { PenSquare, Settings, Menu } from "lucide-react"
import { cn } from "@/lib/utils"

interface Conversation {
  id: number
  title: string
  created_at: string
  updated_at: string
}

interface ChatSidebarProps {
  isOpen?: boolean
  onToggle?: () => void
  conversations?: Conversation[]
  currentConversationId?: number | null
  onNewChat?: () => void
  onSelectConversation?: (id: number) => void
}

export function ChatSidebar({
  isOpen = true,
  onToggle,
  conversations = [],
  currentConversationId,
  onNewChat,
  onSelectConversation,
}: ChatSidebarProps) {
  const router = useRouter()

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    if (date.toDateString() === today.toDateString()) {
      return "Aujourd'hui"
    } else if (date.toDateString() === yesterday.toDateString()) {
      return "Hier"
    } else {
      return date.toLocaleDateString("fr-FR", { day: "numeric", month: "long" })
    }
  }

  const groupedConversations = conversations.reduce(
    (acc, conv) => {
      const dateLabel = formatDate(conv.updated_at)
      if (!acc[dateLabel]) {
        acc[dateLabel] = []
      }
      acc[dateLabel].push(conv)
      return acc
    },
    {} as Record<string, Conversation[]>,
  )

  return (
    <aside
      className={cn(
        "flex h-screen w-64 flex-col border-r border-border bg-sidebar transition-all duration-300",
        !isOpen && "w-0 overflow-hidden",
      )}
    >
      <div className="flex items-center justify-between p-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-foreground text-background">
            <span className="text-sm font-bold">M</span>
          </div>
          <span className="text-lg font-semibold">Memory AI</span>
        </div>
        {onToggle && (
          <Button variant="ghost" size="icon" onClick={onToggle} className="lg:hidden">
            <Menu className="h-5 w-5" />
          </Button>
        )}
      </div>

      <div className="px-3 pb-3">
        <Button variant="secondary" className="w-full justify-start gap-2" size="sm" onClick={onNewChat}>
          <PenSquare className="h-4 w-4" />
          Nouvelle conversation
        </Button>
      </div>

      <div className="px-3 pb-3">
        <Button
          variant="ghost"
          className="w-full justify-start gap-2"
          size="sm"
          onClick={() => router.push("/settings")}
        >
          <Settings className="h-4 w-4" />
          Paramètres
        </Button>
      </div>

      <ScrollArea className="flex-1 px-3 scrollbar-visible overflow-y-auto">

        <div className="space-y-4">
          {Object.entries(groupedConversations).map(([dateLabel, convs]) => (
            <div key={dateLabel}>
              <h3 className="mb-2 px-2 text-xs font-medium text-muted-foreground">{dateLabel}</h3>
              <div className="space-y-1">
                {convs.map((conv) => (
                  <Button
                    key={conv.id}
                    variant={currentConversationId === conv.id ? "secondary" : "ghost"}
                    className="w-full justify-start text-sm font-normal"
                    size="sm"
                    onClick={() => onSelectConversation?.(conv.id)}
                  >
                    {conv.title}
                  </Button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </ScrollArea>
    </aside>
  )
}
