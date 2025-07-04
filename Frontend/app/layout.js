// Arquivo: frontend/app/layout.js
"use client" // É importante para o Contexto funcionar no App Router

import { Inter as FontSans } from "next/font/google"
import "./globals.css"
import { cn } from "@/lib/utils"
import { AuthProvider } from "@/contexts/AuthContext" // Verifica se esta importação está correta

const fontSans = FontSans({
  subsets: ["latin"],
  variable: "--font-sans",
})

// Remova ou comente o 'export const metadata' se estiver usando "use client"
// export const metadata = { ... }

export default function RootLayout({ children }) {
  return (
    <html lang="pt-br" suppressHydrationWarning>
      <head />
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased",
          fontSans.variable
        )}
      >
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  )
}