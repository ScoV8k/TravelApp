// app/trip/[id]/page.tsx
"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { Chat } from "@/components/chat"
type Message = {
  _id: string
  trip_id: string
  text: string
  isUser: boolean
  timestamp: string
}

export default function TripPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const { id } = useParams()
  const tripId = id as string

  useEffect(() => {
    const token = localStorage.getItem("token")

    async function fetchMessages() {
      if (!id) return; // Dodano sprawdzenie czy id istnieje
      try {
        const res = await fetch(`http://localhost:8000/messages/trip/${id}`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        })
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json()
        setMessages(data)
      } catch (error) {
         console.error("Failed to fetch messages:", error);
         // Opcjonalnie: obsługa błędu w UI
      }
    }

    fetchMessages()
  }, [id])

  return (
    <div className="flex flex-col h-full w-full">
      <div className="flex flex-col h-full w-full  mx-auto">
        <Chat initialMessages={messages} tripId={tripId} />
      </div>
    </div>
  )
}