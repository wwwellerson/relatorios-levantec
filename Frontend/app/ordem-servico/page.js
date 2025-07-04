"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation" // Importamos o hook de navegação
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea" // Usaremos para a descrição
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group" // Para a seleção do tipo de serviço
import { Label } from "@/components/ui/label"
import { ArrowLeft, Loader2, FileSignature } from "lucide-react"

export default function OrdemServicoPage() {
    const [clientes, setClientes] = useState([])
    const [motores, setMotores] = useState([])
    const [clienteSelecionado, setClienteSelecionado] = useState(null)
    const [motorSelecionado, setMotorSelecionado] = useState(null)
    const [tipoServico, setTipoServico] = useState('manutencao'); // 'manutencao' ou 'instalacao'
    const [descricaoServico, setDescricaoServico] = useState('');
    const [isLoading, setIsLoading] = useState(false)
    const router = useRouter(); // Hook para fazer o redirecionamento

    const apiBaseUrl = "http://192.168.1.9:8000";

    // Busca clientes ao carregar a página
    useEffect(() => {
        const fetchClientes = async () => {
            try {
                const response = await fetch(`${apiBaseUrl}/api/clientes`);
                const data = await response.json();
                if (response.ok) setClientes(data);
            } catch (error) { console.error("Falha ao buscar clientes:", error) }
        };
        fetchClientes();
    }, []);

    // Busca motores quando um cliente é selecionado
    useEffect(() => {
        if (!clienteSelecionado) {
            setMotores([]);
            setMotorSelecionado(null);
            return;
        }
        const fetchMotores = async () => {
            try {
                const response = await fetch(`${apiBaseUrl}/api/clientes/${clienteSelecionado.id_cliente}/motores`);
                const data = await response.json();
                if(response.ok) setMotores(data);
            } catch (error) { console.error("Falha ao buscar motores:", error); }
        };
        fetchMotores();
    }, [clienteSelecionado]);

    const handleGerarOS = async () => {
        if (!clienteSelecionado || !motorSelecionado || !descricaoServico) {
            alert("Por favor, preencha todos os campos: Cliente, Motor e Descrição do Serviço.");
            return;
        }
        setIsLoading(true);
        try {
            const dadosOS = {
                id_cliente: clienteSelecionado.id_cliente,
                id_motor: motorSelecionado.id_motor,
                tipo_servico: tipoServico,
                descricao_servico: descricaoServico
            };
            const response = await fetch(`${apiBaseUrl}/api/ordens-servico`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dadosOS)
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.mensagem);
                // Redireciona o usuário para a página de relatórios salvos
                router.push('/relatorios-salvos');
            } else {
                throw new Error(result.detail || "Falha ao gerar a Ordem de Serviço.");
            }
        } catch (error) {
            alert(`Erro: ${error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-100 p-4 md:p-8">
            <div className="max-w-4xl mx-auto">
                <Card>
                    <CardHeader>
                        <CardTitle className="text-2xl font-bold text-blue-600">Gerar Ordem de Serviço</CardTitle>
                        <CardDescription>Preencha os dados abaixo para criar uma nova OS.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="p-4 border rounded-lg">
                            <h3 className="font-semibold mb-4 text-lg">1. Seleção de Cliente e Equipamento</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <Label className="block mb-2">Cliente</Label>
                                    <Select onValueChange={(value) => setClienteSelecionado(clientes.find(c => c.id_cliente.toString() === value))}>
                                        <SelectTrigger><SelectValue placeholder="Selecione o cliente..." /></SelectTrigger>
                                        <SelectContent>{clientes.map((c) => (<SelectItem key={c.id_cliente} value={c.id_cliente.toString()}>{c.nome_cliente}</SelectItem>))}</SelectContent>
                                    </Select>
                                </div>
                                <div>
                                    <Label className="block mb-2">Motor/Equipamento</Label>
                                    <Select onValueChange={(value) => setMotorSelecionado(motores.find(m => m.id_motor === value))} disabled={!clienteSelecionado}>
                                        <SelectTrigger><SelectValue placeholder={!clienteSelecionado ? "Selecione um cliente..." : "Selecione o motor..."} /></SelectTrigger>
                                        <SelectContent>{motores.map((m) => (<SelectItem key={m.id_motor} value={m.id_motor}>{m.descricao_motor}</SelectItem>))}</SelectContent>
                                    </Select>
                                </div>
                            </div>
                        </div>

                        <div className="p-4 border rounded-lg">
                             <h3 className="font-semibold mb-4 text-lg">2. Detalhes do Serviço</h3>
                             <div className="space-y-4">
                                <div>
                                    <Label className="block mb-2">Tipo de Serviço</Label>
                                    <RadioGroup defaultValue="manutencao" onValueChange={setTipoServico}>
                                        <div className="flex items-center space-x-2"><RadioGroupItem value="instalacao" id="r1" /><Label htmlFor="r1">Instalação de novo sistema</Label></div>
                                        <div className="flex items-center space-x-2"><RadioGroupItem value="manutencao" id="r2" /><Label htmlFor="r2">Manutenção de sistema</Label></div>
                                    </RadioGroup>
                                </div>
                                <div>
                                     <Label htmlFor="descricao" className="block mb-2">Descrição dos Serviços Realizados</Label>
                                     <Textarea id="descricao" placeholder="Descreva aqui detalhadamente o serviço que foi executado..." value={descricaoServico} onChange={(e) => setDescricaoServico(e.target.value)} />
                                </div>
                             </div>
                        </div>
                        
                        <div className="flex gap-4 pt-4 border-t">
                            <Link href="/" className="flex-1"><Button variant="outline" className="w-full" disabled={isLoading}><ArrowLeft className="mr-2 h-4 w-4" />Voltar</Button></Link>
                            <Button onClick={handleGerarOS} className="flex-1" disabled={isLoading}>
                                {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileSignature className="mr-2 h-4 w-4" />}
                                {isLoading ? 'Gerando OS...' : 'Gerar e Enviar OS'}
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}