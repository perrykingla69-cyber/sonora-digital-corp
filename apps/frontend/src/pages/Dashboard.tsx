import { useAuth } from "@/_core/hooks/useAuth";
import { useLocation } from "wouter";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { trpc } from "@/lib/trpc";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from "recharts";
import { TrendingUp, Users, DollarSign, Zap, Send, Sparkles } from "lucide-react";

const DEMO_BAR_ID = 1; // Conrado Botanero

export default function Dashboard() {
  const { user, isAuthenticated } = useAuth();
  const [, setLocation] = useLocation();
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const getDashboardMetrics = trpc.conrado.getDashboardMetrics.useQuery(
    { barId: DEMO_BAR_ID },
    { enabled: isAuthenticated }
  );

  const runSwarmCycle = trpc.conrado.runSwarmCycle.useMutation();
  const launchPromotion = trpc.conrado.launchPromotion.useMutation();

  useEffect(() => {
    if (!isAuthenticated) {
      setLocation("/");
      return;
    }

    if (getDashboardMetrics.data) {
      setMetrics(getDashboardMetrics.data);
      setLoading(false);
    }
  }, [isAuthenticated, getDashboardMetrics.data, setLocation]);

  const handleRunSwarm = async () => {
    try {
      await runSwarmCycle.mutateAsync({ barId: DEMO_BAR_ID });
      // Refetch metrics
      getDashboardMetrics.refetch();
    } catch (error) {
      console.error("Error running swarm:", error);
    }
  };

  const handleLaunchPromotion = async () => {
    try {
      // Launch promotion on menu item 1 with 15% discount
      await launchPromotion.mutateAsync({ barId: DEMO_BAR_ID, menuItemId: 1, discountPercentage: 15 });
      getDashboardMetrics.refetch();
    } catch (error) {
      console.error("Error launching promotion:", error);
    }
  };

  // Demo data for charts
  const hourlyData = [
    { hour: "18:00", sales: 450, customers: 8 },
    { hour: "19:00", sales: 620, customers: 12 },
    { hour: "20:00", sales: 890, customers: 16 },
    { hour: "21:00", sales: 1200, customers: 22 },
    { hour: "22:00", sales: 1450, customers: 28 },
    { hour: "23:00", sales: 1100, customers: 24 },
    { hour: "00:00", sales: 800, customers: 18 },
  ];

  const vipData = [
    { level: "Normal", count: 8 },
    { level: "Silver", count: 12 },
    { level: "Gold", count: 6 },
    { level: "Diamante", count: 3 },
  ];

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-4">Acceso Requerido</h1>
          <p className="text-purple-300 mb-8">Por favor inicia sesión para acceder al dashboard</p>
          <Button onClick={() => setLocation("/")} className="bg-cyan-500 hover:bg-cyan-600">
            Volver al Inicio
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Header */}
      <div className="border-b border-purple-500/20 bg-slate-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white">Dashboard - Conrado Botanero</h1>
              <p className="text-purple-300 mt-1">📍 Plaza Colossus, Hermosillo | 🕕 Abierto 6PM - 2AM</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-cyan-400">{user?.name}</div>
              <div className="text-sm text-purple-300">{user?.role}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border-cyan-500/30 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm mb-2">Ventas Hoy</p>
                <p className="text-3xl font-bold text-cyan-400">${metrics?.totalRevenue || "0"}</p>
              </div>
              <DollarSign className="w-12 h-12 text-cyan-400/30" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-pink-500/10 to-purple-500/10 border-pink-500/30 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm mb-2">Órdenes</p>
                <p className="text-3xl font-bold text-pink-400">{metrics?.totalOrders || "0"}</p>
              </div>
              <TrendingUp className="w-12 h-12 text-pink-400/30" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/30 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm mb-2">Clientes Activos</p>
                <p className="text-3xl font-bold text-green-400">{metrics?.activeCustomers || "0"}</p>
              </div>
              <Users className="w-12 h-12 text-green-400/30" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border-yellow-500/30 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm mb-2">Ticket Promedio</p>
                <p className="text-3xl font-bold text-yellow-400">${metrics?.avgOrderValue || "0"}</p>
              </div>
              <Zap className="w-12 h-12 text-yellow-400/30" />
            </div>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Sales by Hour */}
          <Card className="bg-slate-900/50 border-purple-500/30 p-6">
            <h3 className="text-lg font-bold text-white mb-4">Ventas por Hora</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={hourlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(168, 85, 247, 0.1)" />
                <XAxis dataKey="hour" stroke="rgba(168, 85, 247, 0.5)" />
                <YAxis stroke="rgba(168, 85, 247, 0.5)" />
                <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid rgba(168, 85, 247, 0.3)" }} />
                <Bar dataKey="sales" fill="#06b6d4" />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          {/* VIP Distribution */}
          <Card className="bg-slate-900/50 border-purple-500/30 p-6">
            <h3 className="text-lg font-bold text-white mb-4">Distribución VIP</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={vipData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(168, 85, 247, 0.1)" />
                <XAxis dataKey="level" stroke="rgba(168, 85, 247, 0.5)" />
                <YAxis stroke="rgba(168, 85, 247, 0.5)" />
                <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid rgba(168, 85, 247, 0.3)" }} />
                <Bar dataKey="count" fill="#a855f7" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>

        {/* Marketing & Agents */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Quick Actions */}
          <Card className="bg-slate-900/50 border-purple-500/30 p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-purple-400" />
              Acciones de Marketing
            </h3>
            <div className="space-y-3">
              <Button
                onClick={handleRunSwarm}
                disabled={runSwarmCycle.isPending}
                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-bold py-2"
              >
                {runSwarmCycle.isPending ? "Ejecutando..." : "🤖 Ejecutar Ciclo Swarm"}
              </Button>
              <Button
                onClick={handleLaunchPromotion}
                disabled={launchPromotion.isPending}
                className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-bold py-2"
              >
                {launchPromotion.isPending ? "Lanzando..." : "🔥 Lanzar Promoción"}
              </Button>
              <Button className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold py-2">
                <Send className="w-4 h-4 mr-2" />
                📱 Enviar Mensaje a Clientes
              </Button>
              <Button className="w-full bg-gradient-to-r from-orange-500 to-red-500 hover:from-orange-600 hover:to-red-600 text-white font-bold py-2">
                <Sparkles className="w-4 h-4 mr-2" />
                🎬 Generar Reels para Redes
              </Button>
            </div>
          </Card>

          {/* Agents Status */}
          <Card className="bg-slate-900/50 border-purple-500/30 p-6">
            <h3 className="text-lg font-bold text-white mb-4">Estado de Agentes IA</h3>
            <div className="space-y-3">
              {[
                { name: "HERMES", status: "Orquestando", color: "from-cyan-400 to-blue-400" },
                { name: "MYSTIC", status: "Prediciendo", color: "from-purple-400 to-pink-400" },
                { name: "REVENUE ENGINE", status: "Optimizando precios", color: "from-green-400 to-emerald-400" },
                { name: "SOCIAL ENGINE", status: "Analizando viralidad", color: "from-yellow-400 to-orange-400" },
                { name: "VIP ENGINE", status: "Actualizando niveles", color: "from-pink-400 to-red-400" },
                { name: "NOTIFY ENGINE", status: "Enviando alertas", color: "from-blue-400 to-cyan-400" },
              ].map((agent, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-purple-500/20">
                  <div>
                    <p className="font-bold text-white">{agent.name}</p>
                    <p className="text-xs text-purple-300">{agent.status}</p>
                  </div>
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Active Mesas */}
        <Card className="bg-slate-900/50 border-purple-500/30 p-6">
          <h3 className="text-lg font-bold text-white mb-4">Mesas Activas</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((mesa) => (
              <div key={mesa} className="bg-slate-800/50 p-4 rounded-lg border border-purple-500/30 hover:border-purple-500/60 transition-all cursor-pointer">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-white">MESA {mesa}</span>
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                </div>
                <p className="text-sm text-purple-300">4 clientes</p>
                <p className="text-sm text-cyan-400 font-bold">${245 + mesa * 50}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
