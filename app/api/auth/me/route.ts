import { NextResponse } from "next/server"
import { cookies } from "next/headers"
import { getUserById } from "@/lib/auth"

export async function GET() {
  try {
    const cookieStore = await cookies()
    const userId = cookieStore.get("userId")?.value

    if (!userId) {
      return NextResponse.json({ user: null })
    }

    const user = await getUserById(Number.parseInt(userId))
    return NextResponse.json({ user })
  } catch (error) {
    console.error("[v0] Get user error:", error)
    return NextResponse.json({ user: null })
  }
}
