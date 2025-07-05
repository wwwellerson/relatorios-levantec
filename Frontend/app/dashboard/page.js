// Arquivo: frontend/app/dashboard/page.js (com a correção da URL da API)
"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ArrowLeft, Upload, FileText, CheckCircle, Loader2 } from "lucide-react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function KpiCard({ title, value, unit }) {
    if (value === null || value === undefined) return null;
    const displayValue = typeof value === 'number' ? value.toFixed(2) : value;
    const displayUnit = unit || '';
    return (
        <Card>
            <CardHeader className="pb-2"><CardTitle className="text-base font-medium">{title}</CardTitle></CardHeader>
            <CardContent><p className="text-2xl font-bold">{displayValue} <span className="text-sm text-muted-foreground">{displayUnit}</span></p></CardContent>
        </Card>
    );
}

function GraficoLinha({ title, data, lines }) {
    if (!data || data.length === 0) return null;
    const formatarTickEixoX = (timeStr) => {
        try {
            const data = new Date(timeStr);
            if (isNaN(data.getTime())) return timeStr;
            const dia = String(data.getDate()).padStart(2, '0');
            const mes = String(data.getMonth() + 1).padStart(2, '0');
            return `${dia}/${mes}`;
        } catch (e) { return timeStr; }
    };
    return (
        <Card>
            <CardHeader><CardTitle>{title}</CardTitle></CardHeader>
            <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                            dataKey="timestamp" 
                            tickFormatter={formatarTickEixoX}
                            angle={-90}
                            textAnchor="end"
                            height={70} 
                            interval={'preserveStartEnd'}
                        />
                        <YAxis domain={['auto', 'auto']} />
                        <Tooltip />
                        <Legend />
                        {lines.map(line => (
                            <Line key={line.dataKey} type="monotone" name={line.name || line.dataKey} dataKey={line.dataKey} stroke={line.stroke} dot={false} strokeWidth={2} />
                        ))}
                    </LineChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}

export default function DashboardPage() {
    const [arquivo, setArquivo] = useState(null);
    const [dadosDashboard, setDadosDashboard] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    // ▼▼▼ AQUI ESTÁ A CORREÇÃO ▼▼▼
    // Usa a variável de ambiente para a URL da API, que funcionará tanto localmente quanto em produção.
    const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;

    const handleAnalisarArquivo = async () => {
        if (!arquivo) {
            alert("Por favor, selecione um arquivo CSV para analisar.");
            return;
        }
        setIsLoading(true); setError(''); setDadosDashboard(null);
        const formData = new FormData();
        formData.append('arquivo_csv', arquivo);
        try {
            const response = await fetch(`${apiBaseUrl}/api/dashboard/analise-instantanea`, { method: 'POST', body: formData });
            const result = await response.json();
            if (response.ok) {
                setDadosDashboard(result);
            } else {
                throw new Error(result.detail || "Falha ao analisar o arquivo.");
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 p-4 md:p-8">
            <div className="max-w-7xl mx-auto space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle className="text-2xl font-bold text-blue-600">Dashboard de Análise Instantânea</CardTitle>
                        <CardDescription>Faça o upload de um arquivo CSV de dados para visualizar os gráficos e indicadores.</CardDescription>
                    </CardHeader>
                    <CardContent className="flex flex-col md:flex-row items-center gap-4">
                        <div className="flex-1 w-full">
                            <Label htmlFor="file-upload" className="flex items-center justify-center w-full h-12 px-4 cursor-pointer bg-white text-blue-600 font-semibold rounded-md border border-blue-300 hover:bg-blue-50">
                                <Upload className="mr-2 h-4 w-4" />
                                {arquivo ? 'Trocar Arquivo' : 'Selecionar Arquivo CSV'}
                            </Label>
                            <Input id="file-upload" type="file" className="hidden" accept=".csv" onChange={(e) => setArquivo(e.target.files[0])} />
                        </div>
                        {arquivo && <div className="flex items-center text-sm text-green-600"><CheckCircle className="mr-2 h-5 w-5" /><span>{arquivo.name}</span></div>}
                        <Button onClick={handleAnalisarArquivo} disabled={!arquivo || isLoading} className="w-full md:w-auto">
                            {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <FileText className="mr-2 h-4 w-4" />}
                            {isLoading ? 'Analisando...' : 'Analisar'}
                        </Button>
                    </CardContent>
                </Card>

                {isLoading && <div className="text-center py-8"><Loader2 className="h-8 w-8 animate-spin mx-auto text-blue-600" /><p className="mt-2">Processando dados...</p></div>}
                {error && <p className="text-center text-red-500">{`Erro: ${error}`}</p>}

                {dadosDashboard && (
                    <div className="space-y-6">
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                            <KpiCard title="Tensão Média (Op.)" value={dadosDashboard.kpis.tensao_media} unit="V" />
                            <KpiCard title="Corrente Média (Op.)" value={dadosDashboard.kpis.corrente_media} unit="A" />
                            <KpiCard title="FP Médio (Op.)" value={dadosDashboard.kpis.fp_medio?.toFixed(3)} unit="" />
                            <KpiCard title="Período Analisado" value={dadosDashboard.kpis.periodo_analisado} unit="" />
                        </div>
                        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                           <KpiCard title="Última Vazão Lida" value={dadosDashboard.kpis.ultima_vazao_lida?.valor} unit={dadosDashboard.kpis.ultima_vazao_lida?.unidade} />
                           <KpiCard title="Vazão Mensal (Acum.)" value={dadosDashboard.kpis.vazao_mensal?.valor} unit={dadosDashboard.kpis.vazao_mensal?.unidade} />
                           <KpiCard title="Vazão da Safra (Total)" value={dadosDashboard.kpis.vazao_safra?.valor} unit={dadosDashboard.kpis.vazao_safra?.unidade} />
                        </div>
                        
                        <Card>
                            <CardHeader><CardTitle>Resumo da Operação</CardTitle></CardHeader>
                            <CardContent><pre className="font-sans text-sm whitespace-pre-wrap bg-gray-100 p-4 rounded-md">{dadosDashboard.kpis.analise_operacao}</pre></CardContent>
                        </Card>

                        <div className="grid grid-cols-1 gap-6">
                            <GraficoLinha title="Gráfico de Tensões" data={dadosDashboard.grafico_tensao} lines={[ { name: 'Fase A', dataKey: 'AVRMS', stroke: '#8884d8' }, { name: 'Fase B', dataKey: 'BVRMS', stroke: '#82ca9d' }, { name: 'Fase C', dataKey: 'CVRMS', stroke: '#ffc658' }]} />
                            <GraficoLinha title="Gráfico de Correntes" data={dadosDashboard.grafico_corrente} lines={[ { name: 'Fase A', dataKey: 'AIRMS', stroke: '#8884d8' }, { name: 'Fase B', dataKey: 'BIRMS', stroke: '#82ca9d' }, { name: 'Fase C', dataKey: 'CIRMS', stroke: '#ffc658' }]} />
                            
                            {/* ▼▼▼ GRÁFICO DE FATOR DE POTÊNCIA RESTAURADO ▼▼▼ */}
                            <GraficoLinha title="Gráfico de Fator de Potência" data={dadosDashboard.grafico_fp} lines={[ { name: 'Fase A', dataKey: 'AFP', stroke: '#8884d8' }, { name: 'Fase B', dataKey: 'BFP', stroke: '#82ca9d' }, { name: 'Fase C', dataKey: 'CFP', stroke: '#ffc658' }]} />

                            <GraficoLinha title="Gráfico de Nível do Reservatório" data={dadosDashboard.grafico_nivel} lines={[{ name: 'Nível', dataKey: 'NIVEL', stroke: '#FF8042' }]} />
                            <GraficoLinha title="Gráfico de Velocidade" data={dadosDashboard.grafico_velocidade} lines={[{ name: 'Velocidade', dataKey: 'VELOCIDADE', stroke: '#00C49F' }]} />
                        </div>
                    </div>
                )}
                 <div className="pt-4 mt-4 border-t">
                    <Link href="/"><Button variant="secondary" className="w-full md:w-auto"><ArrowLeft className="mr-2 h-4 w-4" />Voltar ao Menu Principal</Button></Link>
                </div>
            </div>
        </div>
    )
}