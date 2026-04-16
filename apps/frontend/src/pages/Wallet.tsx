import { useAuth } from "@/_core/hooks/useAuth";
import { useLocation } from "wouter";
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { trpc } from "@/lib/trpc";
import { CreditCard, TrendingUp, Download } from "lucide-react";

const DEMO_BAR_ID = 1;

export default function Wallet() {
  const { user, isAuthenticated } = useAuth();
  const [, setLocation] = useLocation();
  const [loadAmount, setLoadAmount] = useState("100");

  const getWallet = trpc.conrado.getWallet.useQuery({ barId: DEMO_BAR_ID }, { enabled: isAuthenticated });
  const loadCredit = trpc.conrado.loadCredit.useMutation();

  if (!isAuthenticated) {
    setLocation("/");
    return null;
  }

  const handleLoadCredit = async () => {
    try {
      await loadCredit.mutateAsync({ barId: DEMO_BAR_ID, amount: parseFloat(loadAmount) });
      getWallet.refetch();
      setLoadAmount("100");
    } catch (error) {
      console.error("Error loading credit:", error);
    }
  };

  const wallet = getWallet.data;
  const balance = wallet?.creditBalance ? parseFloat(wallet.creditBalance.toString()) : 0;
  const totalLoaded = wallet?.totalLoaded ? parseFloat(wallet.totalLoaded.toString()) : 0;
  const totalSpent = wallet?.totalSpent ? parseFloat(wallet.totalSpent.toString()) : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Header */}
      <div className="border-b border-purple-500/20 bg-slate-900/50 backdrop-blur sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 py-6">
          <div className="flex items-center gap-3 mb-2">
            <CreditCard className="w-8 h-8 text-cyan-400" />
            <h1 className="text-3xl font-bold text-white">Mi Wallet</h1>
          </div>
          <p className="text-purple-300">Crédito interno de Conrado Botanero</p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Balance Card */}
        <Card className="bg-gradient-to-br from-cyan-600/20 to-blue-600/20 border-cyan-500/50 p-8 mb-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <p className="text-purple-300 text-sm mb-2">Saldo Disponible</p>
              <p className="text-4xl font-bold text-cyan-400">${balance.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-purple-300 text-sm mb-2">Total Cargado</p>
              <p className="text-4xl font-bold text-green-400">${totalLoaded.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-purple-300 text-sm mb-2">Total Gastado</p>
              <p className="text-4xl font-bold text-pink-400">${totalSpent.toFixed(2)}</p>
            </div>
          </div>
        </Card>

        {/* Load Credit Section */}
        <Card className="bg-slate-900/50 border-purple-500/30 p-8 mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Cargar Crédito</h2>
          <div className="grid md:grid-cols-2 gap-8">
            {/* Quick Load Buttons */}
            <div>
              <p className="text-purple-300 mb-4">Cargas rápidas</p>
              <div className="grid grid-cols-2 gap-3">
                {[50, 100, 200, 500].map((amount) => (
                  <Button
                    key={amount}
                    onClick={() => setLoadAmount(amount.toString())}
                    variant={loadAmount === amount.toString() ? "default" : "outline"}
                    className={`font-bold py-6 ${
                      loadAmount === amount.toString()
                        ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-white"
                        : "border-purple-500/30 text-purple-300 hover:bg-purple-500/10"
                    }`}
                  >
                    ${amount}
                  </Button>
                ))}
              </div>
            </div>

            {/* Custom Amount */}
            <div>
              <p className="text-purple-300 mb-4">Monto personalizado</p>
              <div className="flex gap-3">
                <div className="flex-1">
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-purple-300">$</span>
                    <input
                      type="number"
                      value={loadAmount}
                      onChange={(e) => setLoadAmount(e.target.value)}
                      className="w-full bg-slate-800/50 border border-purple-500/30 rounded-lg pl-8 pr-4 py-3 text-white placeholder-purple-400 focus:outline-none focus:border-purple-500"
                      placeholder="Ingresa monto"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Load Button */}
          <Button
            onClick={handleLoadCredit}
            disabled={loadCredit.isPending || !loadAmount}
            className="w-full mt-6 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-bold py-4 text-lg"
          >
            {loadCredit.isPending ? "Procesando..." : `💳 Cargar $${loadAmount}`}
          </Button>
        </Card>

        {/* Transaction History */}
        <Card className="bg-slate-900/50 border-purple-500/30 p-8">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-purple-400" />
            Historial de Transacciones
          </h2>

          <div className="space-y-4">
            {[
              { date: "Hoy 22:15", type: "Carga", amount: 100, status: "Completado" },
              { date: "Ayer 20:30", type: "Gasto", amount: -45, status: "Completado" },
              { date: "Ayer 19:45", type: "Gasto", amount: -65, status: "Completado" },
              { date: "Hace 2 días", type: "Carga", amount: 200, status: "Completado" },
              { date: "Hace 3 días", type: "Gasto", amount: -120, status: "Completado" },
            ].map((tx, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-slate-800/30 rounded-lg border border-purple-500/20 hover:border-purple-500/40 transition-all">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${tx.type === "Carga" ? "bg-green-500/20 text-green-400" : "bg-red-500/20 text-red-400"}`}>
                    {tx.type === "Carga" ? "+" : "-"}
                  </div>
                  <div>
                    <p className="font-bold text-white">{tx.type}</p>
                    <p className="text-sm text-purple-300">{tx.date}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className={`font-bold text-lg ${tx.amount > 0 ? "text-green-400" : "text-red-400"}`}>${Math.abs(tx.amount).toFixed(2)}</p>
                  <p className="text-xs text-purple-300">{tx.status}</p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Info Section */}
        <Card className="bg-purple-500/10 border-purple-500/30 p-6 mt-8">
          <div className="flex gap-4">
            <Download className="w-6 h-6 text-purple-400 flex-shrink-0" />
            <div>
              <h3 className="font-bold text-white mb-2">¿Cómo funciona?</h3>
              <ul className="text-sm text-purple-300 space-y-1">
                <li>✓ Carga crédito en tu wallet</li>
                <li>✓ Usa el crédito para pagar órdenes en el bar</li>
                <li>✓ Gana tokens por cada compra</li>
                <li>✓ Sube de nivel VIP y desbloquea recompensas</li>
              </ul>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
