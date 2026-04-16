import { useAuth } from "@/_core/hooks/useAuth";
import { useLocation } from "wouter";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { trpc } from "@/lib/trpc";
import { Crown, Zap, Gift, TrendingUp } from "lucide-react";

const DEMO_BAR_ID = 1;

export default function VIPPage() {
  const { user, isAuthenticated } = useAuth();
  const [, setLocation] = useLocation();

  const getVIPStatus = trpc.conrado.getVIPStatus.useQuery({ barId: DEMO_BAR_ID }, { enabled: isAuthenticated });

  if (!isAuthenticated) {
    setLocation("/");
    return null;
  }

  const vipLevels = [
    {
      name: "Normal",
      minSpending: 0,
      discount: 0,
      perks: ["Acceso al menú QR", "Participación en feed social", "Gana tokens por compras"],
      color: "from-slate-400 to-slate-500",
      icon: "👤",
    },
    {
      name: "Silver",
      minSpending: 500,
      discount: 10,
      perks: ["10% descuento en todas las bebidas", "Acceso a eventos especiales", "Prioridad en mesas", "50 tokens bonus"],
      color: "from-slate-300 to-slate-400",
      icon: "🥈",
    },
    {
      name: "Gold",
      minSpending: 2000,
      discount: 15,
      perks: ["15% descuento", "Acceso a área VIP", "Bebida gratis en cumpleaños", "Invitaciones a eventos exclusivos", "200 tokens bonus"],
      color: "from-yellow-400 to-yellow-500",
      icon: "🥇",
    },
    {
      name: "Diamante",
      minSpending: 5000,
      discount: 20,
      perks: ["20% descuento permanente", "Acceso VIP ilimitado", "Concierge personal", "Eventos privados", "1000 tokens bonus", "Membresía de por vida"],
      color: "from-cyan-300 to-blue-400",
      icon: "💎",
    },
  ];

  const currentLevel = getVIPStatus.data?.currentLevel || "Normal";
  const currentSpending = parseFloat(getVIPStatus.data?.totalSpending?.toString() || "0");
  const currentLevelIndex = vipLevels.findIndex((l) => l.name === currentLevel);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Header */}
      <div className="border-b border-purple-500/20 bg-slate-900/50 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center gap-3 mb-2">
            <Crown className="w-8 h-8 text-yellow-400" />
            <h1 className="text-3xl font-bold text-white">Sistema VIP Gamificado</h1>
          </div>
          <p className="text-purple-300">Tu nivel actual: <span className="font-bold text-yellow-400">{currentLevel}</span> | Gastado: <span className="font-bold text-cyan-400">${currentSpending.toFixed(2)}</span></p>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Current Level Card */}
        <Card className="bg-gradient-to-r from-purple-600/20 to-pink-600/20 border-purple-500/50 p-8 mb-12">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-4xl font-bold text-white mb-2">¡Eres {currentLevel}!</h2>
              <p className="text-purple-300 text-lg">
                {currentLevelIndex < vipLevels.length - 1
                  ? `Faltan $${(vipLevels[currentLevelIndex + 1].minSpending - currentSpending).toFixed(2)} para ser ${vipLevels[currentLevelIndex + 1].name}`
                  : "¡Felicidades! Alcanzaste el máximo nivel"}
              </p>
            </div>
            <div className="text-6xl">{vipLevels[currentLevelIndex].icon}</div>
          </div>

          {/* Progress Bar */}
          <div className="mt-6">
            <div className="w-full bg-slate-800/50 rounded-full h-3 border border-purple-500/30">
              <div
                className="bg-gradient-to-r from-cyan-400 to-purple-400 h-3 rounded-full transition-all"
                style={{
                  width: `${Math.min(100, (currentSpending / (vipLevels[currentLevelIndex + 1]?.minSpending || 5000)) * 100)}%`,
                }}
              ></div>
            </div>
          </div>
        </Card>

        {/* VIP Levels Grid */}
        <div className="mb-12">
          <h3 className="text-2xl font-bold text-white mb-6">Niveles VIP</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {vipLevels.map((level, idx) => (
              <Card
                key={level.name}
                className={`border-2 p-6 transition-all ${
                  currentLevel === level.name
                    ? `bg-gradient-to-br ${level.color} border-white shadow-lg shadow-${level.color.split(" ")[1]}`
                    : "bg-slate-900/50 border-purple-500/30 hover:border-purple-500/60"
                }`}
              >
                <div className="text-4xl mb-3">{level.icon}</div>
                <h4 className="text-xl font-bold text-white mb-2">{level.name}</h4>
                <div className="mb-4">
                  <p className="text-sm text-purple-300">Gasto mínimo</p>
                  <p className="text-2xl font-bold text-cyan-400">${level.minSpending}</p>
                </div>
                <div className="mb-4">
                  <p className="text-sm text-purple-300">Descuento</p>
                  <p className="text-2xl font-bold text-green-400">{level.discount}%</p>
                </div>
                <div className="space-y-2">
                  {level.perks.map((perk, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm text-purple-200">
                      <Zap className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                      <span>{perk}</span>
                    </div>
                  ))}
                </div>
                {currentLevel === level.name && (
                  <Button className="w-full mt-4 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-bold">
                    Tu nivel actual
                  </Button>
                )}
              </Card>
            ))}
          </div>
        </div>

        {/* Rewards Section */}
        <div>
          <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <Gift className="w-6 h-6 text-pink-400" />
            Recompensas Desbloqueadas
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { title: "Bebida Gratis", desc: "Una bebida premium en tu próxima visita", icon: "🍹" },
              { title: "Mesa VIP", desc: "Reserva garantizada en área VIP", icon: "👑" },
              { title: "Tokens Bonus", desc: "500 tokens adicionales", icon: "⭐" },
              { title: "Evento Exclusivo", desc: "Invitación a evento privado", icon: "🎉" },
              { title: "Descuento Especial", desc: "20% en todo durante una noche", icon: "🔥" },
              { title: "Concierge", desc: "Servicio personalizado", icon: "🎩" },
            ].map((reward, i) => (
              <Card key={i} className="bg-slate-900/50 border-purple-500/30 p-6 hover:border-purple-500/60 transition-all">
                <div className="text-4xl mb-3">{reward.icon}</div>
                <h4 className="font-bold text-white mb-2">{reward.title}</h4>
                <p className="text-sm text-purple-300">{reward.desc}</p>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
