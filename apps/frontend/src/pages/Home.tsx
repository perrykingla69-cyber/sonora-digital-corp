import { useAuth } from "@/_core/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getLoginUrl } from "@/const";
import { useLocation } from "wouter";
import { Zap, Users, TrendingUp, Music, QrCode, Sparkles } from "lucide-react";

export default function Home() {
  const { user, isAuthenticated } = useAuth();
  const [, setLocation] = useLocation();

  if (isAuthenticated && user) {
    // Redirect to dashboard
    setLocation("/dashboard");
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: "1s" }}></div>
      </div>

      {/* Navigation */}
      <nav className="relative z-10 flex justify-between items-center px-6 py-4 border-b border-purple-500/20">
        <div className="flex items-center gap-2">
          <Music className="w-8 h-8 text-cyan-400" />
          <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
            CONRADO OS
          </h1>
        </div>
        <div className="text-sm text-purple-300">🍺 Botanero Live</div>
      </nav>

      {/* Main Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 py-20">
        {/* Hero Section */}
        <div className="text-center mb-20">
          <h2 className="text-5xl md:text-6xl font-bold mb-6 text-white">
            Sistema Operativo para <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">Bares Inteligentes</span>
          </h2>
          <p className="text-xl text-purple-200 mb-8 max-w-2xl mx-auto">
            POS digital, red social interna, economía tokenizada y agentes IA que impulsan ventas en tiempo real
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Button
              onClick={() => (window.location.href = getLoginUrl())}
              className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-bold py-3 px-8 rounded-lg shadow-lg shadow-cyan-500/50 transition-all"
            >
              Entrar Ahora
            </Button>
            <Button
              onClick={() => setLocation("/menu")}
              variant="outline"
              className="border-purple-400 text-purple-300 hover:bg-purple-500/10 font-bold py-3 px-8 rounded-lg"
            >
              Ver Menú QR
            </Button>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-3 gap-4 max-w-2xl mx-auto mb-16">
            <Card className="bg-slate-900/50 border-purple-500/30 p-4">
              <div className="text-2xl font-bold text-cyan-400">8</div>
              <div className="text-sm text-purple-300">Mesas Activas</div>
            </Card>
            <Card className="bg-slate-900/50 border-purple-500/30 p-4">
              <div className="text-2xl font-bold text-pink-400">24</div>
              <div className="text-sm text-purple-300">Clientes Hoy</div>
            </Card>
            <Card className="bg-slate-900/50 border-purple-500/30 p-4">
              <div className="text-2xl font-bold text-purple-400">$4.2K</div>
              <div className="text-sm text-purple-300">Ventas Hoy</div>
            </Card>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-20">
          {[
            {
              icon: QrCode,
              title: "POS Digital con QR",
              desc: "Menú interactivo, pedidos sin contacto, pagos instantáneos",
              color: "from-cyan-400 to-blue-400",
            },
            {
              icon: Users,
              title: "Red Social Interna",
              desc: "Feed en vivo, fotos, likes, tokens automáticos por engagement",
              color: "from-pink-400 to-purple-400",
            },
            {
              icon: Sparkles,
              title: "Sistema VIP Gamificado",
              desc: "Niveles: Normal → Silver → Gold → Diamante con recompensas",
              color: "from-yellow-400 to-orange-400",
            },
            {
              icon: Zap,
              title: "Agentes IA Swarm",
              desc: "Hermes, Mystic, Revenue Engine, Social Engine automatizan decisiones",
              color: "from-purple-400 to-pink-400",
            },
            {
              icon: TrendingUp,
              title: "Dashboard en Tiempo Real",
              desc: "Ventas, inventario, clientes activos, métricas clave del negocio",
              color: "from-green-400 to-cyan-400",
            },
            {
              icon: Music,
              title: "Marketing Automático",
              desc: "Promociones dinámicas, notificaciones, campañas con un click",
              color: "from-red-400 to-pink-400",
            },
          ].map((feature, i) => {
            const Icon = feature.icon;
            return (
              <Card
                key={i}
                className="bg-slate-900/50 border-purple-500/30 hover:border-purple-500/60 p-6 transition-all hover:shadow-lg hover:shadow-purple-500/20"
              >
                <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${feature.color} p-3 mb-4`}>
                  <Icon className="w-full h-full text-white" />
                </div>
                <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                <p className="text-sm text-purple-300">{feature.desc}</p>
              </Card>
            );
          })}
        </div>

        {/* Simulation Preview */}
        <Card className="bg-slate-900/50 border-purple-500/30 p-8 mb-20">
          <h3 className="text-2xl font-bold text-white mb-6">Simulación: Noche de Sábado en Conrado Botanero</h3>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div className="bg-slate-800/50 p-4 rounded-lg border border-cyan-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
                  <span className="text-cyan-400 font-bold">MESA 1</span>
                </div>
                <p className="text-sm text-purple-300">4 clientes | $245 consumidos | VIP Gold</p>
              </div>
              <div className="bg-slate-800/50 p-4 rounded-lg border border-pink-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-pink-400 rounded-full animate-pulse"></div>
                  <span className="text-pink-400 font-bold">ÁREA VIP</span>
                </div>
                <p className="text-sm text-purple-300">Alejandro Zamora tocando | 8 clientes Diamante</p>
              </div>
              <div className="bg-slate-800/50 p-4 rounded-lg border border-purple-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
                  <span className="text-purple-400 font-bold">FEED SOCIAL</span>
                </div>
                <p className="text-sm text-purple-300">23 posts | 156 likes | 45 tokens repartidos</p>
              </div>
            </div>
            <div className="space-y-4">
              <div className="bg-slate-800/50 p-4 rounded-lg border border-green-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                  <span className="text-green-400 font-bold">VENTAS</span>
                </div>
                <p className="text-sm text-purple-300">$4,280 | 18 órdenes | Ticket promedio: $238</p>
              </div>
              <div className="bg-slate-800/50 p-4 rounded-lg border border-yellow-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full animate-pulse"></div>
                  <span className="text-yellow-400 font-bold">AGENTES IA</span>
                </div>
                <p className="text-sm text-purple-300">3 promociones activas | Revenue +12% | Hermes orquestando</p>
              </div>
              <div className="bg-slate-800/50 p-4 rounded-lg border border-orange-500/30">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-2 h-2 bg-orange-400 rounded-full animate-pulse"></div>
                  <span className="text-orange-400 font-bold">MARKETING</span>
                </div>
                <p className="text-sm text-purple-300">2 campañas lanzadas | 156 notificaciones enviadas</p>
              </div>
            </div>
          </div>
        </Card>

        {/* Footer CTA */}
        <div className="text-center">
          <h3 className="text-3xl font-bold text-white mb-4">¿Listo para revolucionar tu bar?</h3>
          <p className="text-purple-300 mb-8 max-w-xl mx-auto">
            7 días de prueba gratis. Sin tarjeta de crédito. Acceso completo a todas las funcionalidades.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              onClick={() => (window.location.href = getLoginUrl())}
              className="bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-bold py-4 px-12 rounded-lg shadow-lg shadow-cyan-500/50 transition-all text-lg"
            >
              Comenzar Ahora
            </Button>
            <Button
              onClick={() => setLocation("/dashboard")}
              className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-bold py-4 px-12 rounded-lg shadow-lg shadow-purple-500/50 transition-all text-lg"
            >
              Ver Dashboard
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
