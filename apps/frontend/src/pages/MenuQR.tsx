import { useAuth } from "@/_core/hooks/useAuth";
import { useLocation } from "wouter";
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { trpc } from "@/lib/trpc";
import { ShoppingCart, Plus, Minus, X } from "lucide-react";

const DEMO_BAR_ID = 1;

interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
}

export default function MenuQR() {
  const { user, isAuthenticated } = useAuth();
  const [, setLocation] = useLocation();
  const [tableNumber, setTableNumber] = useState("1");
  const [cart, setCart] = useState<CartItem[]>([]);
  const [showCart, setShowCart] = useState(false);

  const getMenuItems = trpc.conrado.getMenuItems.useQuery({ barId: DEMO_BAR_ID });
  const createOrder = trpc.conrado.createOrder.useMutation();

  if (!isAuthenticated) {
    setLocation("/");
    return null;
  }

  const demoMenuItems = [
    { id: 1, name: "Cerveza Corona", category: "Bebidas", price: 45, description: "Cerveza premium mexicana" },
    { id: 2, name: "Margarita", category: "Cócteles", price: 65, description: "Clásico cóctel mexicano" },
    { id: 3, name: "Tequila Shots", category: "Bebidas", price: 35, description: "Tequila 100% agave" },
    { id: 4, name: "Botanas Mixtas", category: "Alimentos", price: 80, description: "Selección de botanas" },
    { id: 5, name: "Tacos al Pastor", category: "Alimentos", price: 120, description: "3 tacos al pastor" },
    { id: 6, name: "Ceviche", category: "Alimentos", price: 150, description: "Fresco y delicioso" },
    { id: 7, name: "Mezcal Joven", category: "Bebidas", price: 55, description: "Mezcal artesanal" },
    { id: 8, name: "Mojito", category: "Cócteles", price: 60, description: "Refrescante mojito" },
  ];

  const addToCart = (item: any) => {
    const existing = cart.find((c) => c.id === item.id);
    if (existing) {
      setCart(cart.map((c) => (c.id === item.id ? { ...c, quantity: c.quantity + 1 } : c)));
    } else {
      setCart([...cart, { id: item.id, name: item.name, price: item.price, quantity: 1 }]);
    }
  };

  const updateQuantity = (id: number, quantity: number) => {
    if (quantity <= 0) {
      setCart(cart.filter((c) => c.id !== id));
    } else {
      setCart(cart.map((c) => (c.id === id ? { ...c, quantity } : c)));
    }
  };

  const totalAmount = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  const handleCheckout = async () => {
    if (cart.length === 0) return;
    try {
      await createOrder.mutateAsync({
        barId: DEMO_BAR_ID,
        tableNumber,
        items: cart.map((item) => ({ menuItemId: item.id, quantity: item.quantity })),
      });
      setCart([]);
      setShowCart(false);
      // Show success message
      alert("¡Orden enviada! Tu comida llegará pronto.");
    } catch (error) {
      console.error("Error creating order:", error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950">
      {/* Header */}
      <div className="border-b border-purple-500/20 bg-slate-900/50 backdrop-blur sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">📋 Menú Digital</h1>
            <p className="text-purple-300 text-sm">Mesa {tableNumber}</p>
          </div>
          <Button
            onClick={() => setShowCart(!showCart)}
            className="relative bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-bold"
          >
            <ShoppingCart className="w-5 h-5 mr-2" />
            Carrito ({cart.length})
            {cart.length > 0 && (
              <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-6 h-6 flex items-center justify-center">
                {cart.length}
              </span>
            )}
          </Button>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Menu Items */}
          <div className="lg:col-span-2">
            <div className="grid md:grid-cols-2 gap-6">
              {demoMenuItems.map((item) => (
                <Card key={item.id} className="bg-slate-900/50 border-purple-500/30 overflow-hidden hover:border-purple-500/60 transition-all">
                  <div className="p-6">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="font-bold text-white text-lg">{item.name}</h3>
                        <p className="text-xs text-purple-400">{item.category}</p>
                      </div>
                      <span className="text-cyan-400 font-bold text-lg">${item.price}</span>
                    </div>
                    <p className="text-sm text-purple-300 mb-4">{item.description}</p>
                    <Button
                      onClick={() => addToCart(item)}
                      className="w-full bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white font-bold py-2"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Agregar
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* Cart Sidebar */}
          {showCart && (
            <div className="lg:col-span-1">
              <Card className="bg-slate-900/50 border-purple-500/30 p-6 sticky top-24">
                <h2 className="text-xl font-bold text-white mb-4">Tu Carrito</h2>

                {cart.length === 0 ? (
                  <p className="text-purple-300 text-center py-8">Carrito vacío</p>
                ) : (
                  <>
                    <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
                      {cart.map((item) => (
                        <div key={item.id} className="bg-slate-800/50 p-4 rounded-lg border border-purple-500/20">
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-bold text-white">{item.name}</h4>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => updateQuantity(item.id, 0)}
                              className="text-red-400 hover:text-red-300"
                            >
                              <X className="w-4 h-4" />
                            </Button>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-cyan-400">${item.price}</span>
                            <div className="flex items-center gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => updateQuantity(item.id, item.quantity - 1)}
                                className="border-purple-500/30 text-purple-300 hover:bg-purple-500/10 h-6 w-6 p-0"
                              >
                                <Minus className="w-3 h-3" />
                              </Button>
                              <span className="text-white font-bold w-6 text-center">{item.quantity}</span>
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => updateQuantity(item.id, item.quantity + 1)}
                                className="border-purple-500/30 text-purple-300 hover:bg-purple-500/10 h-6 w-6 p-0"
                              >
                                <Plus className="w-3 h-3" />
                              </Button>
                            </div>
                          </div>
                          <div className="text-right text-sm text-purple-300 mt-2">
                            Subtotal: ${(item.price * item.quantity).toFixed(2)}
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Total */}
                    <div className="border-t border-purple-500/20 pt-4 mb-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-purple-300">Subtotal:</span>
                        <span className="text-white font-bold">${totalAmount.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between items-center mb-4">
                        <span className="text-purple-300">Tokens a ganar:</span>
                        <span className="text-yellow-400 font-bold">+{Math.floor(totalAmount / 10)}</span>
                      </div>
                      <div className="flex justify-between items-center text-lg font-bold text-white">
                        <span>Total:</span>
                        <span className="text-cyan-400">${totalAmount.toFixed(2)}</span>
                      </div>
                    </div>

                    {/* Checkout Button */}
                    <Button
                      onClick={handleCheckout}
                      disabled={createOrder.isPending}
                      className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-bold py-3"
                    >
                      {createOrder.isPending ? "Procesando..." : "💳 Pagar Ahora"}
                    </Button>
                  </>
                )}
              </Card>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
