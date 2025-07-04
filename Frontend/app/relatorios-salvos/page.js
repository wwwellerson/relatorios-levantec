// Arquivo: frontend/app/relatorios-salvos/page.js (Versão final com busca e WhatsApp)
"use client"

import { useState, useEffect, useMemo } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ArrowLeft, FileText, Download, Eye, Trash2, Calendar, Mail, Loader2, Search } from "lucide-react"

// Ícone do WhatsApp (SVG) para usarmos no botão
const WhatsAppIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
        <path d="M13.601 2.326A7.85 7.85 0 0 0 7.994 0C3.627 0 .068 3.558.064 7.926c0 1.399.366 2.76 1.057 3.965L0 16l4.204-1.102a7.9 7.9 0 0 0 3.79.965h.004c4.368 0 7.926-3.558 7.93-7.93A7.9 7.9 0 0 0 13.6 2.326zM7.994 14.521a6.6 6.6 0 0 1-3.356-.92l-.24-.144-2.494.654.666-2.433-.156-.251a6.56 6.56 0 0 1-1.007-3.505c0-3.626 2.957-6.584 6.591-6.584a6.56 6.56 0 0 1 4.66 1.931 6.56 6.56 0 0 1 1.928 4.66c-.004 3.639-2.961 6.592-6.592 6.592m3.615-4.934c-.197-.099-1.17-.578-1.353-.646-.182-.065-.315-.099-.445.099-.133.197-.513.646-.627.775-.114.133-.232.148-.43.05-.197-.1-.836-.308-1.592-.985-.59-.525-.985-1.175-1.103-1.372-.114-.198-.011-.304.088-.403.087-.088.197-.232.296-.346.1-.114.133-.198.198-.33.065-.134.034-.248-.015-.347-.05-.099-.445-1.076-.612-1.47-.16-.389-.323-.335-.445-.34-.114-.007-.247-.007-.38-.007a.73.73 0 0 0-.529.247c-.182.198-.691.677-.691 1.654s.71 1.916.81 2.049c.098.133 1.394 2.132 3.383 2.992.47.205.84.326 1.129.418.475.152.904.129 1.246.08.38-.058 1.171-.48 1.338-.943.164-.464.164-.86.114-.943-.049-.084-.182-.133-.38-.232"/>
    </svg>
);

export default function RelatoriosSalvosPage() {
    const [relatorios, setRelatorios] = useState([])
    const [isLoading, setIsLoading] = useState(true);
    const [sendingEmailId, setSendingEmailId] = useState(null);
    const [termoBusca, setTermoBusca] = useState('');
    const [sendingWhatsAppId, setSendingWhatsAppId] = useState(null); // Novo estado para o WhatsApp

    const apiBaseUrl = "http://192.168.1.9:8000";

    const fetchRelatorios = async () => {
        setIsLoading(true);
        try {
            const response = await fetch(`${apiBaseUrl}/api/relatorios-salvos`);
            const data = await response.json();
            if (response.ok) setRelatorios(data);
            else throw new Error(data.detail || "Falha ao buscar relatórios.");
        } catch (error) {
            console.error("Erro ao buscar relatórios salvos:", error);
            alert(`Erro: ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchRelatorios();
    }, []);

    const handleEnviarEmail = async (nome_arquivo) => {
        setSendingEmailId(nome_arquivo);
        try {
            const response = await fetch(`${apiBaseUrl}/api/relatorios-salvos/${nome_arquivo}/enviar-email`, { method: 'POST' });
            const result = await response.json();
            if (response.ok) alert(result.message);
            else throw new Error(result.detail || "Falha ao enviar o e-mail.");
        } catch (error) {
            alert(`Erro: ${error.message}`);
        } finally {
            setSendingEmailId(null);
        }
    };

    const handleExcluir = async (nome_arquivo) => {
        if (!window.confirm(`Tem certeza que deseja excluir o relatório "${nome_arquivo}"?`)) return;
        try {
            const response = await fetch(`${apiBaseUrl}/api/relatorios-salvos/${nome_arquivo}`, { method: 'DELETE' });
            if (response.ok) {
                alert("Relatório excluído com sucesso.");
                fetchRelatorios();
            } else {
                const erro = await response.json();
                throw new Error(erro.detail || "Falha ao excluir o relatório.");
            }
        } catch (error) {
            alert(`Erro: ${error.message}`);
        }
    };
    
    // ▼▼▼ NOVA FUNÇÃO PARA ENVIAR WHATSAPP ▼▼▼
    const handleEnviarWhatsApp = async (nome_arquivo) => {
        setSendingWhatsAppId(nome_arquivo);
        try {
            const response = await fetch(`${apiBaseUrl}/api/relatorios-salvos/${nome_arquivo}/enviar-whatsapp`, {
                method: 'POST',
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
            } else {
                throw new Error(result.detail || "Falha ao enviar mensagem de WhatsApp.");
            }
        } catch (error) {
            alert(`Erro: ${error.message}`);
        } finally {
            setSendingWhatsAppId(null);
        }
    };

    const relatoriosFiltrados = useMemo(() => {
        if (!termoBusca) return relatorios;
        return relatorios.filter(relatorio =>
            relatorio.nome_arquivo?.toLowerCase().includes(termoBusca.toLowerCase()) ||
            relatorio.cliente?.toLowerCase().includes(termoBusca.toLowerCase()) ||
            relatorio.motor?.toLowerCase().includes(termoBusca.toLowerCase())
        );
    }, [relatorios, termoBusca]);

    return (
        <div className="min-h-screen bg-gray-100 p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                <Card>
                    <CardHeader>
                        <CardTitle className="text-2xl font-bold text-center text-blue-600">RELATÓRIOS E OS GERADOS</CardTitle>
                        <CardDescription className="text-center">Busque e gerencie os arquivos gerados.</CardDescription>
                        <div className="relative pt-4">
                            <Search className="absolute left-2.5 top-6 h-4 w-4 text-muted-foreground" />
                            <Input
                                type="search"
                                placeholder="Buscar por nome do arquivo, cliente ou motor..."
                                className="w-full rounded-lg bg-background pl-8"
                                value={termoBusca}
                                onChange={(e) => setTermoBusca(e.target.value)}
                            />
                        </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {isLoading ? (
                            <div className="flex justify-center items-center py-8"><Loader2 className="h-8 w-8 animate-spin text-blue-600" /><p className="ml-4 text-gray-500">Carregando...</p></div>
                        ) : relatoriosFiltrados.length === 0 ? (
                            <div className="text-center py-8"><FileText className="mx-auto h-16 w-16 text-gray-400 mb-4" /><p>Nenhum arquivo encontrado.</p></div>
                        ) : (
                            <div className="space-y-3">
                                {relatoriosFiltrados.map((relatorio) => (
                                    <Card key={relatorio.nome_arquivo} className="border-l-4 border-l-blue-500">
                                        <CardContent className="p-4 flex flex-col md:flex-row items-start md:items-center justify-between">
                                            <div className="flex-1 overflow-hidden mb-4 md:mb-0">
                                                <h3 className="font-semibold text-lg truncate" title={relatorio.nome_arquivo}>{relatorio.nome_arquivo}</h3>
                                                <p className="text-sm text-gray-600 truncate">{relatorio.cliente} / {relatorio.motor}</p>
                                                <div className="flex items-center text-xs text-gray-500 mt-2"><Calendar className="mr-1 h-4 w-4" />{relatorio.data} • {relatorio.tamanho_mb}</div>
                                            </div>
                                            <div className="flex gap-2 ml-0 md:ml-4 flex-shrink-0">
                                                <a href={`${apiBaseUrl}/api/relatorios-salvos/${relatorio.nome_arquivo}`} target="_blank" rel="noopener noreferrer"><Button title="Visualizar" size="sm" variant="outline"><Eye className="h-4 w-4" /></Button></a>
                                                <a href={`${apiBaseUrl}/api/relatorios-salvos/${relatorio.nome_arquivo}`} download><Button title="Baixar" size="sm" variant="outline"><Download className="h-4 w-4" /></Button></a>
                                                <Button title="Enviar por E-mail" size="sm" variant="outline" onClick={() => handleEnviarEmail(relatorio.nome_arquivo)} disabled={sendingEmailId === relatorio.nome_arquivo}>{sendingEmailId === relatorio.nome_arquivo ? <Loader2 className="h-4 w-4 animate-spin" /> : <Mail className="h-4 w-4" />}</Button>
                                                
                                                {/* ▼▼▼ NOVO BOTÃO DE WHATSAPP ADICIONADO AQUI ▼▼▼ */}
                                                <Button title="Enviar por WhatsApp" size="sm" variant="outline" onClick={() => handleEnviarWhatsApp(relatorio.nome_arquivo)} disabled={sendingWhatsAppId === relatorio.nome_arquivo}>
                                                    {sendingWhatsAppId === relatorio.nome_arquivo ? <Loader2 className="h-4 w-4 animate-spin" /> : <WhatsAppIcon />}
                                                </Button>

                                                <Button title="Excluir" size="sm" variant="destructive" onClick={() => handleExcluir(relatorio.nome_arquivo)}><Trash2 className="h-4 w-4" /></Button>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        )}
                        <div className="pt-4 border-t">
                            <Link href="/"><Button variant="secondary" className="w-full md:w-auto"><ArrowLeft className="mr-2 h-4 w-4" />Voltar ao Menu</Button></Link>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}