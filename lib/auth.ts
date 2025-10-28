import bcrypt from "bcryptjs"
import { query } from "./db"

export interface User {
  id: number
  username: string
  email: string
  created_at: Date
}

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10)
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash)
}

export async function createUser(username: string, email: string, password: string): Promise<User> {
  const passwordHash = await hashPassword(password)
  const result = await query<any>("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)", [
    username,
    email,
    passwordHash,
  ])
  return {
    id: result.insertId,
    username,
    email,
    created_at: new Date(),
  }
}

export async function getUserByEmail(email: string): Promise<(User & { password_hash: string }) | null> {
  const users = await query<any[]>("SELECT * FROM users WHERE email = ?", [email])
  return users.length > 0 ? users[0] : null
}

export async function getUserById(id: number): Promise<User | null> {
  const users = await query<any[]>("SELECT id, username, email, created_at FROM users WHERE id = ?", [id])
  return users.length > 0 ? users[0] : null
}
