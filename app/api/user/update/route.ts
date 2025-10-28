import { NextResponse } from "next/server"
import { cookies } from "next/headers"
import { query } from "@/lib/db"
import { hashPassword } from "@/lib/auth"

export async function PUT(request: Request) {
  try {
    const cookieStore = await cookies()
    const userId = cookieStore.get("userId")?.value

    if (!userId) {
      return NextResponse.json({ error: "Non authentifié" }, { status: 401 })
    }

    const { username, email, password } = await request.json()

    if (password) {
      const passwordHash = await hashPassword(password)
      await query("UPDATE users SET username = ?, email = ?, password_hash = ? WHERE id = ?", [
        username,
        email,
        passwordHash,
        userId,
      ])
    } else {
      await query("UPDATE users SET username = ?, email = ? WHERE id = ?", [username, email, userId])
    }

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("[v0] Update user error:", error)
    return NextResponse.json({ error: "Erreur lors de la mise à jour" }, { status: 500 })
  }
}
