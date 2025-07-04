// Arquivo: frontend/app/estoque/page.js (Versão final com busca e alerta visual)
"use client"

import { useState, useEffect, useMemo } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogClose } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ArrowLeft, PlusCircle, Edit, Trash2, Loader2, FileDown, Search, AlertTriangle } from "lucide-react"

// --- Formulário para Adicionar/Editar Componente ---
function FormularioComponente({ onSave, registroInicial, isEditMode }) {
    const [formData, setFormData] = useState({});

    useEffect(() => {
        const defaultState = {
            modelo_componente: '', nome_componente: '', especificacao: '',
            quantidade: '', localizacao: ''
        };
        setFormData(isEditMode && registroInicial ? registroInicial : defaultState);
    }, [registroInicial, isEditMode]);

    const handleChange = (e) => {
        const { id, value } = e.target;
        setFormData(prev => ({ ...prev, [id]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSave(formData);
    };

    return (
        <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 py-4">
                <div className="space-y-2">
                    <Label htmlFor="modelo_componente">Modelo do Componente</Label>
                    <Input id="modelo_componente" value={formData.modelo_componente || ''} onChange={handleChange} />
                </div>
                <div className="space-y-2"><Label htmlFor="nome_componente">Nome do Componente</Label><Input id="nome_componente" value={formData.nome_componente || ''} onChange={handleChange} /></div>
                <div className="space-y-2"><Label htmlFor="especificacao">Especificação</Label><Input id="especificacao" value={formData.especificacao || ''} onChange={handleChange} /></div>
                <div className="space-y-2"><Label htmlFor="quantidade">Quantidade</Label><Input id="quantidade" type="number" value={formData.quantidade || ''} onChange={handleChange} /></div>
                <div className="space-y-2 col-span-full"><Label htmlFor="localizacao">Localização</Label><Input id="localizacao" value={formData.localizacao || ''} onChange={handleChange} /></div>
            </div>
            <DialogFooter>
                <DialogClose asChild><Button type="button" variant="secondary">Cancelar</Button></DialogClose>
                <Button type="submit">Salvar</Button>
            </DialogFooter>
        </form>
    );
}

// --- Página Principal do Estoque ---
export default function EstoquePage() {
    const [componentes, setComponentes] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [isDialogOpen, setDialogOpen] = useState(false);
    const [termoBusca, setTermoBusca] = useState(''); // Estado para a busca
    const [registroSelecionado, setRegistroSelecionado] = useState(null);
    const [isEditMode, setIsEditMode] = useState(false);

    const LIMITE_ESTOQUE_BAIXO = 5;
    const apiBaseUrl = "http://192.168.1.9:8000";

    const fetchEstoque = async () => {
        setIsLoading(true);
        try {
            const response = await fetch(`${apiBaseUrl}/api/estoque`);
            const data = await response.json();
            if (response.ok) setComponentes(data);
            else throw new Error(data.detail || "Falha ao buscar o estoque.");
        } catch (error) {
            alert(`Erro: ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => { fetchEstoque() }, []);

    const handleAdicionar = () => {
        setIsEditMode(false);
        setRegistroSelecionado(null);
        setDialogOpen(true);
    };

    const handleEditar = (componente) => {
        setIsEditMode(true);
        setRegistroSelecionado(componente);
        setDialogOpen(true);
    };

    const handleSave = async (formData) => {
        const quantidade = parseInt(formData.quantidade, 10) || 0;
        if (!isEditMode) {
            const componenteExistente = componentes.find(c => c.modelo_componente.toLowerCase() === formData.modelo_componente.toLowerCase().trim());
            if (componenteExistente) {
                const confirmar = window.confirm(`O componente "${formData.modelo_componente}" já existe. Deseja somar ${quantidade} unidades ao estoque?`);
                if (!confirmar) return;
            }
        }
        const dadosParaEnviar = { ...formData, quantidade };
        const url = isEditMode ? `${apiBaseUrl}/api/estoque/${registroSelecionado.modelo_componente}` : `${apiBaseUrl}/api/estoque`;
        const method = isEditMode ? 'PUT' : 'POST'; // No futuro, usaremos PUT para editar
        try {
            const response = await fetch(url, { method: method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(dadosParaEnviar) });
            const result = await response.json();
            if (response.ok) {
                alert(result.mensagem);
                setDialogOpen(false);
                fetchEstoque();
            } else { throw new Error(result.detail || "Falha ao salvar componente."); }
        } catch (error) { alert(`Erro: ${error.message}`); }
    };

    const handleExcluir = async (modelo) => {
        if (!window.confirm(`Tem certeza que deseja excluir o componente "${modelo}"?`)) return;
        try {
            const response = await fetch(`${apiBaseUrl}/api/estoque/${modelo}`, { method: 'DELETE' });
            if (response.ok) {
                alert("Componente removido com sucesso.");
                fetchEstoque();
            } else {
                const erro = await response.json();
                throw new Error(erro.detail || "Falha ao excluir.");
            }
        } catch (error) { alert(`Erro: ${error.message}`); }
    };

    const handleExportarPDF = async () => {
        try {
            const response = await fetch(`${apiBaseUrl}/api/estoque/exportar-pdf`);
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `Relatorio_Estoque_${new Date().toISOString().slice(0,10)}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            } else {
                const erro = await response.json();
                throw new Error(erro.detail || "Falha ao exportar PDF.");
            }
        } catch (error) { alert(`Erro: ${error.message}`); }
    };

    const componentesFiltrados = useMemo(() => {
        if (!termoBusca) return componentes;
        return componentes.filter(item =>
            item.modelo_componente?.toLowerCase().includes(termoBusca.toLowerCase()) ||
            item.nome_componente?.toLowerCase().includes(termoBusca.toLowerCase()) ||
            item.especificacao?.toLowerCase().includes(termoBusca.toLowerCase())
        );
    }, [componentes, termoBusca]);

    return (
        <div className="min-h-screen bg-gray-100 p-4 md:p-8">
            <div className="max-w-7xl mx-auto">
                <Card>
                    <CardHeader>
                        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                            <div><CardTitle className="text-2xl font-bold text-blue-600">CONTROLE DE ESTOQUE</CardTitle><CardDescription>Busque, adicione e gerencie seus componentes.</CardDescription></div>
                            <div className="flex w-full md:w-auto gap-2">
                                <Button variant="outline" onClick={handleExportarPDF} className="w-full md:w-auto"><FileDown className="mr-2 h-4 w-4" />Exportar PDF</Button>
                                <Button onClick={handleAdicionar} className="w-full md:w-auto"><PlusCircle className="mr-2 h-4 w-4" />Adicionar</Button>
                            </div>
                        </div>
                        <div className="relative mt-4"><Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" /><Input type="search" placeholder="Buscar por modelo, nome ou especificação..." className="w-full pl-8" value={termoBusca} onChange={(e) => setTermoBusca(e.target.value)} /></div>
                    </CardHeader>
                    <CardContent>
                        {isLoading ? ( <div className="text-center py-8"><Loader2 className="h-8 w-8 animate-spin mx-auto" /></div> ) : (
                            <Table>
                                <TableHeader><TableRow><TableHead>Modelo</TableHead><TableHead>Nome</TableHead><TableHead>Especificação</TableHead><TableHead className="text-center">Qtd.</TableHead><TableHead className="text-right">Ações</TableHead></TableRow></TableHeader>
                                <TableBody>
                                    {componentesFiltrados.map((item) => {
                                        const estoqueBaixo = item.quantidade <= LIMITE_ESTOQUE_BAIXO;
                                        return (
                                            <TableRow key={item.modelo_componente} className={estoqueBaixo ? 'bg-red-100 hover:bg-red-200' : ''}>
                                                <TableCell className="font-mono">{item.modelo_componente}</TableCell>
                                                <TableCell>{item.nome_componente}</TableCell>
                                                <TableCell>{item.especificacao}</TableCell>
                                                <TableCell className={`text-center font-bold ${estoqueBaixo ? 'text-red-600' : ''}`}>
                                                    {estoqueBaixo && <AlertTriangle className="h-4 w-4 inline-block mr-2 text-red-500" />}
                                                    {item.quantidade}
                                                </TableCell>
                                                <TableCell className="text-right space-x-2">
                                                    <Button variant="outline" size="icon" onClick={() => handleEditar(item)}><Edit className="h-4 w-4" /></Button>
                                                    <Button variant="destructive" size="icon" onClick={() => handleExcluir(item.modelo_componente)}><Trash2 className="h-4 w-4" /></Button>
                                                </TableCell>
                                            </TableRow>
                                        );
                                    })}
                                </TableBody>
                            </Table>
                        )}
                         {componentesFiltrados.length === 0 && !isLoading && ( <p className="text-center py-8">Nenhum componente encontrado.</p> )}
                    </CardContent>
                </Card>
                 <div className="pt-4 mt-4 border-t">
                    <Link href="/"><Button variant="secondary" className="w-full md:w-auto"><ArrowLeft className="mr-2 h-4 w-4" />Voltar</Button></Link>
                </div>
            </div>
            <Dialog open={isDialogOpen} onOpenChange={setDialogOpen}>
                <DialogContent className="sm:max-w-2xl"><DialogHeader><DialogTitle>{isEditMode ? 'Editar Componente' : 'Adicionar / Atualizar Estoque'}</DialogTitle></DialogHeader><FormularioComponente onSave={handleSave} registroInicial={registroSelecionado} isEditMode={isEditMode} /></DialogContent>
            </Dialog>
        </div>
    )
}