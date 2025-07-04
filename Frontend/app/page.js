// Arquivo: frontend/app/page.js (Versão final e completa)
"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { FileText, Users, FolderOpen, Archive } from "lucide-react"

export default function HomePage() {
  const buttonStyle = "w-full h-14 text-lg justify-start bg-gray-900 text-primary-foreground hover:bg-gray-700"

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-800">Sistema de Relatórios</CardTitle>
          <p className="text-gray-500 mt-2">Selecione uma opção para começar</p>
        </CardHeader>
        <CardContent className="space-y-4 p-6">
          <Link href="/novo-relatorio" className="block">
            <Button className={buttonStyle}>
              <FileText className="mr-3 h-6 w-6" />
              Gerar Relatório Técnico
            </Button>
          </Link>
          
          <Link href="/ordem-servico" className="block">
            <Button className={buttonStyle}>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-3 h-6 w-6"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline><path d="m10.4 12.6-1.8 1.8-1.8-1.8"></path><path d="M8.6 14.4V8"></path><path d="m15.4 15.6-1.8-1.8-1.8 1.8"></path><path d="M13.6 17.4V12"></path></svg>
              Gerar Ordem de Serviço
            </Button>
          </Link>

          {/* ▼▼▼ BOTÃO DO DASHBOARD CORRIGIDO ▼▼▼ */}
          <Link href="/dashboard" className="block">
            <Button className={buttonStyle}>
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-3 h-6 w-6"><path d="M3 3v18h18"/><path d="M18.7 8a6 6 0 0 0-6-6"/><path d="M13 13a4 4 0 1 1 4 4"/></svg>
              Dashboard de Análise
            </Button>
          </Link>

          <Link href="/editar-clientes" className="block">
            <Button className={buttonStyle}>
              <Users className="mr-3 h-6 w-6" />
              Gerir Clientes e Motores
            </Button>
          </Link>
          
          <Link href="/estoque" className="block">
            <Button className={buttonStyle}>
              <Archive className="mr-3 h-6 w-6" />
              Controle de Estoque
            </Button>
          </Link>

          <Link href="/relatorios-salvos" className="block">
            <Button className={buttonStyle}>
              <FolderOpen className="mr-3 h-6 w-6" />
              Visualizar Arquivos Gerados
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  )
}