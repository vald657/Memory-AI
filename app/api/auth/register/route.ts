import { NextResponse } from "next/server"
import { createUser, getUserByEmail } from "@/lib/auth"

export async function POST(request: Request) {
  try {
    const { username, email, password } = await request.json()

    if (!username || !email || !password) {
      return NextResponse.json({ error: "Tous les champs sont requis" }, { status: 400 })
    }

    const existingUser = await getUserByEmail(email)
    if (existingUser) {
      return NextResponse.json({ error: "Cet email est déjà utilisé" }, { status: 400 })
    }

    const user = await createUser(username, email, password)

    return NextResponse.json({ user }, { status: 201 })
  } catch (error) {
    console.error("[v0] Registration error:", error)
    return NextResponse.json({ error: "Erreur lors de l'inscription" }, { status: 500 })
  }
}
