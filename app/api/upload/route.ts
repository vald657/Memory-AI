import { NextResponse } from "next/server"
import { cookies } from "next/headers"

export async function POST(request: Request) {
  try {
    const cookieStore = await cookies()
    const userId = cookieStore.get("userId")?.value

    if (!userId) {
      return NextResponse.json({ error: "Non authentifié" }, { status: 401 })
    }

    const formData = await request.formData()
    const file = formData.get("file") as File

    if (!file) {
      return NextResponse.json({ error: "Aucun fichier fourni" }, { status: 400 })
    }

    const allowedTypes = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        { error: "Type de fichier non autorisé. Seuls les PDF et DOCX sont acceptés." },
        { status: 400 },
      )
    }

    // Ici, vous devriez sauvegarder le fichier sur le serveur ou dans un service de stockage
    // Pour l'instant, on retourne juste les informations du fichier
    const fileInfo = {
      name: file.name,
      type: file.type,
      size: file.size,
    }

    return NextResponse.json({ file: fileInfo })
  } catch (error) {
    console.error("[v0] Upload error:", error)
    return NextResponse.json({ error: "Erreur lors de l'upload" }, { status: 500 })
  }
}
