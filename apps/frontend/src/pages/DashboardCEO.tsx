import { useAuth } from "@/_core/hooks/useAuth";
import { useLocation } from "wouter";
import { useEffect, useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, CheckCircle, AlertTriangle, Users, TrendingUp, Database } from "lucide-react";

// Demo data: 6 tenants
const DEMO_TENANTS = [
  {
    id: "tenant-1",
    name: "Restaurante El Faro",
    plan: "Pro",
    status: "healthy",
    users: 8,
    apiCalls: 12540,
    storage: "2.3GB / 10GB",
    lastSync: "hace 2 min",
    alerts: 0,
  },
  {
    id: "tenant-2",
    name: "Panadería Don Juan",
    plan: "Starter",
    status: "healthy",
    users: 3,
    apiCalls: 1240,
    storage: "450MB / 5GB",
    lastSync: "hace 5 min",
    alerts: 1,
  },
  {
    id: "tenant-3",
    name: "Consultoría Fiscal MX",
    plan: "Enterprise",
    status: "warning",
    users: 15,
    apiCalls: 45600,
    storage: "8.9GB / 50GB",
    lastSync: "hace 1 min",
    alerts: 2,
  },
  {
    id: "tenant-4",
    name: "Boutique Minerva",
    plan: "Pro",
    status: "healthy",
    users: 5,
    apiCalls: 5320,
    storage: "1.2GB / 10GB",
    lastSync: "hace 3 min",
    alerts: 0,
  },
  {
    id: "tenant-5",
    name: "Bufete Legal Torres",
    plan: "Enterprise",
    status: "healthy",
    users: 12,
    apiCalls: 32100,
    storage: "15.6GB / 50GB",
    lastSync: "hace 1 min",
    alerts: 3,
  },
  {
    id: "tenant-6",
    name: "Farmacia Moderna",
    plan: "Pro",
    status: "offline",
    users: 6,
    apiCalls: 0,
    storage: "800MB / 10GB",
    lastSync: "hace 47 min",
    alerts: 5,
  },
];

export default function DashboardCEO() {
  const { user, isAuthenticated } = useAuth();
  const [, setLocation] = useLocation();

  useEffect(() => {
    if (!isAuthenticated) {
      setLocation("/");
    }
  }, [isAuthenticated, setLocation]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-4">Acceso Requerido</h1>
          <p className="text-purple-300 mb-8">Por favor inicia sesión como administrador</p>
          <Button onClick={() => setLocation("/")} className="bg-cyan-500 hover:bg-cyan-600">
            Volver al Inicio
          </Button>
        </div>
      </div>
    );
  }

  const healthyCount = DEMO_TENANTS.filter((t) => t.status === "healthy").length;
  const warningCount = DEMO_TENANTS.filter((t) => t.status === "warning").length;
  const offlineCount = DEMO_TENANTS.filter((t) => t.status === "offline").length;
  const totalAlerts = DEMO_TENANTS.reduce((sum, t) => sum + t.alerts, 0);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "bg-green-500/20 text-green-400 border-green-500/30";
      case "warning":
        return "bg-yellow-500/20 text-yellow-400 border-yellow-500/30";
      case "offline":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      default:
        return "bg-slate-500/20 text-slate-400 border-slate-500/30";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy":
        return <CheckCircle className="w-4 h-4" />;
      case "warning":
        return <AlertTriangle className="w-4 h-4" />;
      case "offline":
        return <AlertCircle className="w-4 h-4" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Header */}
      <div className="border-b border-purple-500/20 bg-slate-900/50 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-white">Dashboard CEO</h1>
              <p className="text-purple-300 mt-1">Control de 6 tenants activos</p>
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
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/10 border-green-500/30 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm mb-2">Saludables</p>
                <p className="text-3xl font-bold text-green-400">{healthyCount}</p>
              </div>
              <CheckCircle className="w-12 h-12 text-green-400/30" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border-yellow-500/30 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm mb-2">Advertencias</p>
                <p className="text-3xl font-bold text-yellow-400">{warningCount}</p>
              </div>
              <AlertTriangle className="w-12 h-12 text-yellow-400/30" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-red-500/10 to-pink-500/10 border-red-500/30 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm mb-2">Desconectados</p>
                <p className="text-3xl font-bold text-red-400">{offlineCount}</p>
              </div>
              <AlertCircle className="w-12 h-12 text-red-400/30" />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border-cyan-500/30 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-300 text-sm mb-2">Alertas Activas</p>
                <p className="text-3xl font-bold text-cyan-400">{totalAlerts}</p>
              </div>
              <AlertCircle className="w-12 h-12 text-cyan-400/30" />
            </div>
          </Card>
        </div>

        {/* Tenants Table */}
        <Card className="bg-slate-900/50 border-purple-500/30 p-6 mb-8">
          <h2 className="text-xl font-bold text-white mb-6">Tenants</h2>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-purple-500/20">
                  <th className="px-4 py-3 text-left text-purple-300 text-sm font-semibold">Nombre</th>
                  <th className="px-4 py-3 text-left text-purple-300 text-sm font-semibold">Plan</th>
                  <th className="px-4 py-3 text-left text-purple-300 text-sm font-semibold">Estado</th>
                  <th className="px-4 py-3 text-left text-purple-300 text-sm font-semibold">Usuarios</th>
                  <th className="px-4 py-3 text-left text-purple-300 text-sm font-semibold">API Calls</th>
                  <th className="px-4 py-3 text-left text-purple-300 text-sm font-semibold">Storage</th>
                  <th className="px-4 py-3 text-left text-purple-300 text-sm font-semibold">Alertas</th>
                  <th className="px-4 py-3 text-left text-purple-300 text-sm font-semibold">Última Sync</th>
                  <th className="px-4 py-3 text-right text-purple-300 text-sm font-semibold">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {DEMO_TENANTS.map((tenant) => (
                  <tr key={tenant.id} className="border-b border-purple-500/10 hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3 text-white text-sm font-medium">{tenant.name}</td>
                    <td className="px-4 py-3 text-purple-300 text-sm">
                      <Badge variant="outline" className="text-xs">
                        {tenant.plan}
                      </Badge>
                    </td>
                    <td className="px-4 py-3">
                      <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-medium ${getStatusColor(tenant.status)}`}>
                        {getStatusIcon(tenant.status)}
                        {tenant.status === "healthy" && "Saludable"}
                        {tenant.status === "warning" && "Advertencia"}
                        {tenant.status === "offline" && "Desconectado"}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-cyan-400 text-sm flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      {tenant.users}
                    </td>
                    <td className="px-4 py-3 text-purple-300 text-sm flex items-center gap-1">
                      <TrendingUp className="w-4 h-4" />
                      {tenant.apiCalls.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-purple-300 text-sm flex items-center gap-1">
                      <Database className="w-4 h-4" />
                      {tenant.storage}
                    </td>
                    <td className="px-4 py-3">
                      {tenant.alerts > 0 && (
                        <Badge variant="destructive" className="text-xs">
                          {tenant.alerts}
                        </Badge>
                      )}
                      {tenant.alerts === 0 && <span className="text-green-400 text-xs">—</span>}
                    </td>
                    <td className="px-4 py-3 text-purple-300 text-xs">{tenant.lastSync}</td>
                    <td className="px-4 py-3 text-right">
                      <Button variant="ghost" size="sm" className="text-cyan-400 hover:text-cyan-300 h-8 px-2">
                        Ver
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>

        {/* System Health & Alerts */}
        <div className="grid md:grid-cols-2 gap-6">
          <Card className="bg-slate-900/50 border-purple-500/30 p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-400" />
              Alertas Críticas (MYSTIC)
            </h3>
            <div className="space-y-2">
              {[
                { tenant: "Farmacia Moderna", msg: "Sin conexión por 47 min", severity: "critical" },
                { tenant: "Consultoría Fiscal MX", msg: "CPU al 87%, aumentar recursos", severity: "warning" },
                { tenant: "Bufete Legal Torres", msg: "3 errores en últimas 24h", severity: "warning" },
              ].map((alert, i) => (
                <div key={i} className="p-3 bg-slate-800/50 rounded-lg border border-purple-500/20 text-sm">
                  <div className="font-bold text-white">{alert.tenant}</div>
                  <div className="text-purple-300 text-xs mt-1">{alert.msg}</div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="bg-slate-900/50 border-purple-500/30 p-6">
            <h3 className="text-lg font-bold text-white mb-4">Acciones Rápidas</h3>
            <div className="space-y-2">
              <Button className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white text-sm">
                🔄 Sincronizar Todos
              </Button>
              <Button className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white text-sm">
                📊 Generar Reporte
              </Button>
              <Button className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white text-sm">
                💬 Chat HERMES
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
