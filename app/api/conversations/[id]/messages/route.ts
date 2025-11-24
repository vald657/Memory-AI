import { NextResponse } from "next/server"
import { cookies } from "next/headers"
import { query } from "@/lib/db"

export async function GET(request: Request, { params }: { params: Promise<{ id: string }> }) {
  try {
    const cookieStore = await cookies()
    const userId = cookieStore.get("userId")?.value
    if (!userId) return NextResponse.json({ error: "Non authentifié" }, { status: 401 })

    const { id } = await params
    const conversations = await query<any[]>("SELECT * FROM conversations WHERE id = ? AND user_id = ?", [id, userId])
    if (conversations.length === 0) return NextResponse.json({ error: "Conversation non trouvée" }, { status: 404 })

    const messages = await query<any[]>("SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC", [id])
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
    if (!userId) return NextResponse.json({ error: "Non authentifié" }, { status: 401 })

    const { id } = await params
    const { role, content, attachments } = await request.json()

    // Vérifier la conversation
    const conversations = await query<any[]>("SELECT * FROM conversations WHERE id = ? AND user_id = ?", [id, userId])
    if (conversations.length === 0) return NextResponse.json({ error: "Conversation non trouvée" }, { status: 404 })

    // 1️⃣ Enregistrer le message utilisateur
    const result = await query<any>(
      "INSERT INTO messages (conversation_id, role, content, attachments) VALUES (?, ?, ?, ?)",
      [id, role, content, attachments ? JSON.stringify(attachments) : null]
    )

    // 2️⃣ Appeler FastAPI pour générer la réponse IA si c’est un message user
    let aiResponse = null
    if (role === "user") {
      try {
        const fastapiRes = await fetch(`http://localhost:8000/ask?prompt=${encodeURIComponent(content)}`)
        const data = await fastapiRes.json()
        aiResponse = data.response || "Aucune réponse disponible."

        // 3️⃣ Enregistrer la réponse IA
        await query(
          "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
          [id, "assistant", aiResponse]
        )
      } catch (error) {
        console.error("Erreur FastAPI:", error)
      }
    }

    return NextResponse.json({
      message_id: result.insertId,
      ai_response: aiResponse,
    }, { status: 201 })
  } catch (error) {
    console.error("[v0] Create message error:", error)
    return NextResponse.json({ error: "Erreur lors de la création du message" }, { status: 500 })
  }
}
