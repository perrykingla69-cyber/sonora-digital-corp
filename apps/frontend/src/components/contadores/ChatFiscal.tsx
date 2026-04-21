'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageCircle } from 'lucide-react';

interface Message {
  id: string;
  rol: 'usuario' | 'hermes';
  contenido: string;
  timestamp: Date;
}

export default function ChatFiscal() {
  const [mensajes, setMensajes] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [mensajes]);

  const enviar = async () => {
    if (!input.trim()) return;

    const nuevoMensaje: Message = {
      id: Date.now().toString(),
      rol: 'usuario',
      contenido: input,
      timestamp: new Date()
    };

    setMensajes(prev => [...prev, nuevoMensaje]);
    setInput('');
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const res = await fetch('/api/v1/agents/hermes/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          mensaje: input,
          contexto: 'contador'
        })
      });

      if (!res.ok) throw new Error('Error en respuesta');
      const data = await res.json();

      setMensajes(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        rol: 'hermes',
        contenido: data.respuesta || 'No pude procesar tu pregunta',
        timestamp: new Date()
      }]);
    } catch (err) {
      console.error('Error:', err);
      setMensajes(prev => [...prev, {
        id: (Date.now() + 1).toString(),
        rol: 'hermes',
        contenido: 'Error conectando con HERMES. Intenta de nuevo.',
        timestamp: new Date()
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 rounded-lg bg-slate-800 border border-slate-700 flex flex-col h-96">
      <div className="flex items-center gap-2 mb-4">
        <MessageCircle className="w-5 h-5 text-blue-400" />
        <h2 className="text-xl font-bold text-white">Pregunta a HERMES</h2>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 mb-3 pr-2">
        {mensajes.length === 0 ? (
          <p className="text-slate-500 text-sm text-center mt-8">
            Pregunta sobre obligaciones, cálculos o regulaciones
          </p>
        ) : (
          mensajes.map(msg => (
            <div
              key={msg.id}
              className={`flex ${msg.rol === 'usuario' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs px-3 py-2 rounded-lg text-sm ${
                  msg.rol === 'usuario'
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-slate-100'
                }`}
              >
                {msg.contenido}
              </div>
            </div>
          ))
        )}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-700 text-slate-100 px-3 py-2 rounded-lg text-sm">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyPress={e => e.key === 'Enter' && enviar()}
          placeholder="¿Preguntas sobre fiscal?"
          disabled={loading}
          className="flex-1 px-3 py-2 rounded-lg bg-slate-700 border border-slate-600 text-white placeholder-slate-500 text-sm disabled:opacity-50"
        />
        <button
          onClick={enviar}
          disabled={loading || !input.trim()}
          className="px-3 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white rounded-lg transition"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
