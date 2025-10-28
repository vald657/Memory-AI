import { NextResponse } from "next/server"
import { cookies } from "next/headers"
import { query } from "@/lib/db"

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const cookieStore = await cookies()
    const userId = cookieStore.get("userId")?.value

    if (!userId) {
      return NextResponse.json({ error: "Non authentifié" }, { status: 401 })
    }

    const { id } = await params

    // Vérifier que la conversation appartient à l'utilisateur
    const conversations = await query<any[]>("SELECT * FROM conversations WHERE id = ? AND user_id = ?", [id, userId])

    if (conversations.length === 0) {
      return NextResponse.json({ error: "Conversation non trouvée" }, { status: 404 })
    }

    const messages = await query<any[]>("SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC", [
      id,
    ])

    const parsedMessages = messages.map((message) => ({
      ...message,
      attachments: message.attachments ? JSON.parse(message.attachments) : [],
    }))

    return NextResponse.json({ messages: parsedMessages })
  } catch (error) {
    console.error("[v0] Get messages error:", error)
    return NextResponse.json({ error: "Erreur lors de la récupération des messages" }, { status: 500 })
  }
}

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const cookieStore = await cookies()
    const userId = cookieStore.get("userId")?.value

    if (!userId) {
      return NextResponse.json({ error: "Non authentifié" }, { status: 401 })
    }

    const { id } = await params
    const { role, content, attachments } = await request.json()

    // Vérifier que la conversation appartient à l'utilisateur
    const conversations = await query<any[]>("SELECT * FROM conversations WHERE id = ? AND user_id = ?", [id, userId])

    if (conversations.length === 0) {
      return NextResponse.json({ error: "Conversation non trouvée" }, { status: 404 })
    }

    const existingMessages = await query<any[]>("SELECT COUNT(*) as count FROM messages WHERE conversation_id = ?", [
      id,
    ])

    const isFirstMessage = existingMessages[0].count === 0

    const result = await query<any>(
      "INSERT INTO messages (conversation_id, role, content, attachments) VALUES (?, ?, ?, ?)",
      [id, role, content, attachments ? JSON.stringify(attachments) : null],
    )

    if (isFirstMessage && role === "user") {
      // Extraire les 50 premiers caractères du message pour le titre
      const title = content.length > 50 ? content.substring(0, 50) + "..." : content
      await query("UPDATE conversations SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", [title, id])
    } else {
      // Mettre à jour seulement la date de modification
      await query("UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", [id])
    }

    const message = {
      id: result.insertId,
      conversation_id: Number.parseInt(id),
      role,
      content,
      attachments,
      created_at: new Date(),
    }

    return NextResponse.json({ message }, { status: 201 })
  } catch (error) {
    console.error("[v0] Create message error:", error)
    return NextResponse.json({ error: "Erreur lors de la création du message" }, { status: 500 })
  }
}
