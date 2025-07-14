"use client"

import { useEffect, useState, useRef } from "react"
import { Textarea } from "@/components/ui/textarea"
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"

type Message = {
  _id?: string
  trip_id?: string
  text: string
  link?: string
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

  useEffect(() => {
    if (initialMessages && initialMessages.length > 0) {
      setMessages(initialMessages)
    }
  }, [initialMessages])

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages, isSending])

  const sendMessage = async () => {
    if (!input.trim() || isSending) return
    
    const currentInput = input
    setInput("")
    
    const timestamp = new Date().toISOString()
    const userMessage: Message = {
      _id: `user-${timestamp}`, 
      trip_id: activeTripId,
      text: currentInput,
      isUser: true,
      timestamp,
    }
    setMessages((prev) => [...prev, userMessage])
    setIsSending(true)

    let currentTripId = activeTripId

    try {
      if (!currentTripId) {
        const userId = localStorage.getItem("user_id")
        const token = localStorage.getItem("token")
        const tripRes = await fetch("http://localhost:8000/trips/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            user_id: userId,
            name: "New Trip",
            status: "draft",
            created_at: new Date().toISOString(),
          }),
        })
        if (!tripRes.ok) throw new Error("Failed to create trip")
        const tripData = await tripRes.json()
        currentTripId = tripData._id
        setActiveTripId(currentTripId)

        setMessages(prev => prev.map(msg => msg._id === userMessage._id ? {...msg, trip_id: currentTripId} : msg));
      }
      
      const messageToSendToDb = { ...userMessage, trip_id: currentTripId, _id: undefined };

      await fetch(`http://localhost:8000/messages/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(messageToSendToDb),
      })

      const lastMessages = [...messages, userMessage]
        .slice(-3)
        .map((msg) => ({
          text: msg.text,
          isUser: msg.isUser,
          timestamp: msg.timestamp,
        }))

      const res = await fetch(
        "http://localhost:8001/generate-message-and-update-information/",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            trip_id: currentTripId,
            user_message: currentInput,
            last_messages: lastMessages,
          }),
        }
      )
      if (!res.ok) {
        const errorText = await res.text()
        console.error(
          "Błąd w /generate-message-and-update-information/:",
          res.status,
          errorText
        )
        throw new Error("Failed to get bot response or update plan")
      }

      const data = await res.json()
      const botMessage: Message = {
        trip_id: currentTripId,
        text: data.bot_response.text,
        isUser: false,
        link: data.bot_response.link,
        timestamp: new Date().toISOString(),
      }

      console.log(botMessage)
      
      await fetch(`http://localhost:8000/messages/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(botMessage),
      })
      
      setMessages((prev) => [...prev, botMessage])

      console.log("✅ Plan updated:", data.updated_plan)

    } catch (error) {
      console.error("Błąd przy wysyłaniu wiadomości:", error)
      setInput(currentInput)
      setMessages((prev) =>
        prev.filter((msg) => msg._id !== userMessage._id)
      )
    } finally {
      setIsSending(false)
    }
  }

  return (
    <div className="flex flex-col w-full h-full overflow-hidden">
      <div className="flex-1 overflow-y-auto w-full px-6 py-4">
        <div className="max-w-3xl mx-auto space-y-4 h-full flex flex-col">
          {messages.length === 0 && !isSending ? (
            <div className="flex flex-1 items-center justify-center">
              <h1 className="text-3xl font-semibold text-muted-foreground text-center">
                Start planning your trip ✈️
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
                  style={{
                    overflowWrap: "break-word",
                    wordBreak: "break-word",
                  }}
                >
                  {msg.text}
                  
                  {msg.link && !msg.isUser && (
            <div className="mt-2">
                <Button
                    onClick={() => window.open(msg.link, "_blank")}
                    size="sm"
                    className="bg-gray-500 hover:bg-gray-700 text-white"
                >
                    Book your flight ✈️
                </Button>
            </div>
        )}
                </div>
              ))}
              
              {isSending && (
                <div className="w-full break-words text-foreground flex items-center gap-2">
                   <div className="flex items-center space-x-1 p-3 rounded-lg bg-gray-100 dark:bg-gray-800">
                      <span className="block w-2 h-2 bg-gray-500 rounded-full animate-pulse [animation-delay:-0.3s]"></span>
                      <span className="block w-2 h-2 bg-gray-500 rounded-full animate-pulse [animation-delay:-0.15s]"></span>
                      <span className="block w-2 h-2 bg-gray-500 rounded-full animate-pulse"></span>
                    </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </>
          )}
        </div>
      </div>

      <div className="p-4 w-full">
        <div className="max-w-2xl mx-auto flex items-start gap-x-4 border-t border-border/50 pt-4">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask question..."
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
            {isSending ? (
              <Loader2 className="animate-spin h-5 w-5" />
            ) : (
              "Send"
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}