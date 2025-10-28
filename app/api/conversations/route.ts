import { NextResponse } from "next/server"
import { cookies } from "next/headers"
import { query } from "@/lib/db"

export async function GET() {
  try {
    const cookieStore = await cookies()
    const userId = cookieStore.get("userId")?.value

    if (!userId) {
      return NextResponse.json({ error: "Non authentifié" }, { status: 401 })
    }

    const conversations = await query<any[]>("SELECT * FROM conversations WHERE user_id = ? ORDER BY updated_at DESC", [
      userId,
    ])

    return NextResponse.json({ conversations })
  } catch (error) {
    console.error("[v0] Get conversations error:", error)
    return NextResponse.json({ error: "Erreur lors de la récupération des conversations" }, { status: 500 })
  }
}

export async function POST(request: Request) {
  try {
    const cookieStore = await cookies()
    const userId = cookieStore.get("userId")?.value

    if (!userId) {
      return NextResponse.json({ error: "Non authentifié" }, { status: 401 })
    }

    const { title } = await request.json()

    const result = await query<any>("INSERT INTO conversations (user_id, title) VALUES (?, ?)", [
      userId,
      title || "Nouvelle conversation",
    ])

    const conversation = {
      id: result.insertId,
      user_id: Number.parseInt(userId),
      title: title || "Nouvelle conversation",
      created_at: new Date(),
      updated_at: new Date(),
    }

    return NextResponse.json({ conversation }, { status: 201 })
  } catch (error) {
    console.error("[v0] Create conversation error:", error)
    return NextResponse.json({ error: "Erreur lors de la création de la conversation" }, { status: 500 })
  }
}
