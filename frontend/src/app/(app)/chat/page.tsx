'use client'

import { useState, useRef, useEffect } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

type RecordingState = 'idle' | 'recording' | 'processing'

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: '¡Hola! Soy Hermes, tu asistente fiscal. ¿En qué te puedo ayudar hoy?',
      timestamp: new Date(),
    },
  ])
  const [inputText, setInputText] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [recordingState, setRecordingState] = useState<RecordingState>('idle')

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const appendMessage = (role: 'user' | 'assistant', content: string) => {
    setMessages((prev) => [
      ...prev,
      {
        id: `${Date.now()}-${Math.random()}`,
        role,
        content,
        timestamp: new Date(),
      },
    ])
  }

  const sendToAI = async (text: string) => {
    if (!text.trim()) return
    appendMessage('user', text)
    setInputText('')
    setIsProcessing(true)

    try {
      const res = await fetch('/api/api/brain/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: text }),
      })
      const data = await res.json()
      const answer =
        data?.answer ?? data?.response ?? data?.text ?? 'Sin respuesta del servidor.'
      appendMessage('assistant', answer)
    } catch {
      appendMessage('assistant', 'Error al conectar con el servidor. Verifica tu conexión.')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleSend = () => {
    if (inputText.trim() && !isProcessing) {
      sendToAI(inputText)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Voice recording
  const handleMicToggle = async () => {
    if (recordingState === 'recording') {
      // Stop recording
      mediaRecorderRef.current?.stop()
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const mediaRecorder = new MediaRecorder(stream)
      mediaRecorderRef.current = mediaRecorder
      audioChunksRef.current = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data)
      }

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop())
        setRecordingState('processing')

        const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' })
        const formData = new FormData()
        formData.append('file', blob, 'audio.webm')

        try {
          const res = await fetch('/api/media/stt', {
            method: 'POST',
            body: formData,
          })
          const data = await res.json()
          const transcript = data?.text ?? data?.transcript ?? ''
          if (transcript) {
            await sendToAI(transcript)
          } else {
            appendMessage('assistant', 'No se pudo transcribir el audio. Intenta de nuevo.')
          }
        } catch {
          appendMessage('assistant', 'Error al procesar el audio.')
        } finally {
          setRecordingState('idle')
        }
      }

      mediaRecorder.start()
      setRecordingState('recording')
    } catch {
      appendMessage('assistant', 'No se pudo acceder al micrófono. Verifica los permisos.')
    }
  }

  // Camera / photo OCR
  const handleCameraClick = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // Reset input so same file can be re-selected
    e.target.value = ''

    appendMessage('user', `[Imagen enviada: ${file.name}]`)
    setIsProcessing(true)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('/api/media/ocr', {
        method: 'POST',
        body: formData,
      })
      const data = await res.json()
      const extracted = data?.text ?? data?.content ?? ''
      if (extracted) {
        await sendToAI(`Analiza este texto extraído de una imagen:\n\n${extracted}`)
      } else {
        appendMessage('assistant', 'No se pudo extraer texto de la imagen.')
      }
    } catch {
      appendMessage('assistant', 'Error al procesar la imagen.')
    } finally {
      setIsProcessing(false)
    }
  }

  const formatTime = (date: Date) =>
    date.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' })

  return (
    <div className="flex flex-col h-[100dvh] bg-[#0A0A0A] text-white overflow-hidden">
      {/* Header */}
      <header className="flex-none flex items-center gap-3 px-4 py-3 border-b border-[#2A2A2A] bg-[#111111]">
        <div className="w-8 h-8 rounded-full bg-[#D4AF37]/20 flex items-center justify-center text-[#D4AF37] font-bold text-sm select-none">
          M
        </div>
        <div>
          <p className="text-sm font-semibold text-[#D4AF37] leading-none">Hermes AI</p>
          <p className="text-xs text-white/40 mt-0.5">Asistente Fiscal</p>
        </div>
        {isProcessing && (
          <span className="ml-auto text-xs text-[#D4AF37]/70 animate-pulse">
            Procesando…
          </span>
        )}
      </header>

      {/* Messages area */}
      <main className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`max-w-[85%] px-4 py-2.5 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-[#D4AF37]/10 text-[#D4AF37] rounded-br-sm'
                  : 'bg-white/5 text-white/90 rounded-bl-sm'
              }`}
            >
              {msg.content}
            </div>
            <span className="text-[10px] text-white/25 mt-1 px-1">
              {formatTime(msg.timestamp)}
            </span>
          </div>
        ))}

        {/* Typing indicator */}
        {isProcessing && (
          <div className="flex items-start">
            <div className="bg-white/5 px-4 py-3 rounded-2xl rounded-bl-sm flex gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-[#D4AF37]/60 animate-bounce [animation-delay:0ms]" />
              <span className="w-1.5 h-1.5 rounded-full bg-[#D4AF37]/60 animate-bounce [animation-delay:150ms]" />
              <span className="w-1.5 h-1.5 rounded-full bg-[#D4AF37]/60 animate-bounce [animation-delay:300ms]" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </main>

      {/* Recording indicator */}
      {recordingState === 'recording' && (
        <div className="flex-none flex items-center justify-center gap-2 py-2 bg-red-900/20 border-t border-red-800/30">
          <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
          <span className="text-xs text-red-400">Grabando… toca el micrófono para detener</span>
        </div>
      )}

      {/* Input bar */}
      <footer className="flex-none flex items-center gap-2 px-3 py-3 border-t border-[#2A2A2A] bg-[#111111]">
        {/* Mic button */}
        <button
          type="button"
          onClick={handleMicToggle}
          disabled={isProcessing || recordingState === 'processing'}
          aria-label="Grabar voz"
          className={`flex-none w-10 h-10 rounded-full flex items-center justify-center transition-colors disabled:opacity-40 ${
            recordingState === 'recording'
              ? 'bg-red-500/20 text-red-400 ring-1 ring-red-500/50'
              : 'bg-white/5 text-white/60 hover:bg-white/10 hover:text-white'
          }`}
        >
          🎤
        </button>

        {/* Camera button */}
        <button
          type="button"
          onClick={handleCameraClick}
          disabled={isProcessing || recordingState !== 'idle'}
          aria-label="Enviar foto"
          className="flex-none w-10 h-10 rounded-full bg-white/5 text-white/60 hover:bg-white/10 hover:text-white flex items-center justify-center transition-colors disabled:opacity-40"
        >
          📷
        </button>

        {/* Hidden file input for photo */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          capture="environment"
          className="hidden"
          onChange={handleFileChange}
        />

        {/* Text input */}
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isProcessing || recordingState !== 'idle'}
          placeholder="Escribe tu pregunta fiscal…"
          className="flex-1 min-w-0 bg-white/5 border border-[#2A2A2A] rounded-full px-4 py-2 text-sm text-white placeholder-white/30 focus:outline-none focus:border-[#D4AF37]/50 focus:bg-white/8 transition-colors disabled:opacity-40"
        />

        {/* Send button */}
        <button
          type="button"
          onClick={handleSend}
          disabled={!inputText.trim() || isProcessing || recordingState !== 'idle'}
          aria-label="Enviar mensaje"
          className="flex-none w-10 h-10 rounded-full bg-[#D4AF37] text-[#0A0A0A] font-bold flex items-center justify-center transition-opacity disabled:opacity-30 hover:opacity-90 active:scale-95"
        >
          ↑
        </button>
      </footer>
    </div>
  )
}
