// components/chat.tsx lub ścieżka do Twojego komponentu Chat
"use client"

import { useEffect, useState, useRef } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"

type Message = {
  _id?: string
  trip_id?: string
  text: string
  isUser: boolean
  timestamp: string
}

type ChatProps = {
  initialMessages?: Message[]
  tripId?: string
}

export const Chat = ({ initialMessages = [], tripId }: ChatProps) => {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [input, setInput] = useState("")
  const [isSending, setIsSending] = useState(false)
  const [activeTripId, setActiveTripId] = useState<string | undefined>(tripId)

  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Efekty useEffect bez zmian...
  useEffect(() => {
    if (initialMessages && initialMessages.length > 0) {
      setMessages(initialMessages)
    }
  }, [initialMessages])
  
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages])

  // Funkcja sendMessage bez zmian...
  const sendMessage = async () => {
    if (!input.trim() || isSending) return
    setIsSending(true)
    let currentTripId = activeTripId
    const currentInput = input;
    setInput(""); 

    try {
      if (!currentTripId) {
        const userId = localStorage.getItem("user_id")
        const token = localStorage.getItem("token")
        const tripRes = await fetch("http://localhost:8000/trips/", {
          method: "POST",
          headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
          body: JSON.stringify({ user_id: userId, name: "New Trip", status: "draft", created_at: new Date().toISOString()}),
        })
        if (!tripRes.ok) throw new Error('Failed to create trip');
        const tripData = await tripRes.json()
        currentTripId = tripData._id
        setActiveTripId(currentTripId)
      }

      const timestamp = new Date().toISOString()
      const userMessage: Message = { trip_id: currentTripId, text: currentInput, isUser: true, timestamp }
      setMessages((prev) => [...prev, userMessage]) // Optymistyczne UI

      const userMsgPromise = fetch(`http://localhost:8000/messages/`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(userMessage),
      });
      const botResponsePromise = fetch("http://127.0.0.1:8001/generuj/", {
         method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ message: currentInput }),
      });
      
      const [userMsgRes, botRes] = await Promise.all([userMsgPromise, botResponsePromise]);

      if (!userMsgRes.ok) {
        console.error("❌ Błąd przy zapisie user message");
        throw new Error('Failed to save user message');
      }
      if (!botRes.ok) {
        console.error("❌ Błąd przy odpowiedzi bota");
        throw new Error('Failed to get bot response');
      }
      

      const botData = await botRes.json()
      const botMessage: Message = { trip_id: currentTripId, text: botData.response, isUser: false, timestamp: new Date().toISOString() }
      
      await fetch(`http://localhost:8000/messages/`, {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(botMessage),
      })
      setMessages((prev) => [...prev, botMessage])
      
      console.log(currentTripId)
      
      const updateRes = await fetch("http://127.0.0.1:8001/update-plan/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          trip_id: currentTripId,
          last_user_message: userMessage.text,
          bot_response: botMessage.text
        })
      });
      
      if (!updateRes.ok) {
        const errorText = await updateRes.text();
        console.error("❌ Błąd w /update-plan/:", updateRes.status, errorText);
      } else {
        const updateData = await updateRes.json();
        console.log("✅ Plan zaktualizowany:", updateData);
      }
      
      
      
      

      // await fetch("http://127.0.0.1:8001/update-plan/", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({
      //     trip_id: currentTripId,
      //     chat_history: [...messages, userMessage, botMessage].map(m => m.text)
      //   })
      // })
      

    } catch (error) {
      console.error("Błąd przy wysyłaniu wiadomości:", error)
      setInput(currentInput); 
      setMessages(prev => prev.filter(msg => msg.text !== currentInput || !msg.isUser)); 
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="flex flex-col w-full h-full overflow-hidden">
      {/* WIADOMOŚCI */}
      <div className="flex-1 overflow-y-auto w-full px-6 py-4">
  <div className="max-w-3xl mx-auto space-y-4 h-full flex flex-col">
    {messages.length === 0 ? (
      <div className="flex flex-1 items-center justify-center">
        <h1 className="text-3xl font-semibold text-muted-foreground text-center">
          Zacznij planować swoją podróż ✈️
        </h1>
      </div>
    ) : (
      <>
        {messages.map((msg) => (
          <div
            key={msg._id || msg.timestamp + msg.text}
            className={
              msg.isUser
                ? "ml-auto w-fit max-w-md break-words rounded-lg bg-gray-200 px-4 py-2 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
                : "w-full break-words text-foreground"
            }
            style={{ overflowWrap: "break-word", wordBreak: "break-word" }}
          >
            {msg.text}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </>
    )}
  </div>
</div>

  
      {/* INPUT NA DOLE */}
      <div className="p-4 w-full">
        <div className="max-w-2xl mx-auto flex items-start gap-x-4 border-t border-border/50 pt-4">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Zadaj pytanie..."
            className="resize-none grow text-sm pl-2"
            rows={1}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault()
                sendMessage()
              }
            }}
          />
          <Button
            onClick={sendMessage}
            disabled={isSending || !input.trim()}
            size="lg"
            className="shrink-0"
          >
            {isSending ? <Loader2 className="animate-spin h-5 w-5" /> : "Wyślij"}
          </Button>
        </div>

      </div>
    </div>
  )

}