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

import { useTrip } from "@/app/context/TripContext"

export default function TripPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const { setTripName, setTripId } = useTrip()
  const { id } = useParams()
  const tripId = id as string

  useEffect(() => {
    const token = localStorage.getItem("token")
    setTripId(tripId) 

    async function fetchMessages() {
      if (!id) return
      try {
        const [msgRes, tripRes] = await Promise.all([
          fetch(`http://localhost:8000/messages/trip/${id}`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
          fetch(`http://localhost:8000/trips/${id}`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ])

        const [messagesData, tripData] = await Promise.all([
          msgRes.json(),
          tripRes.json(),
        ])

        setMessages(messagesData)
        setTripName(tripData.name)
      } catch (err) {
        console.error("Błąd przy pobieraniu danych:", err)
      }
    }

    fetchMessages()
}, [tripId, setTripId, setTripName])

  return (
    <div className="flex flex-col h-full w-full">
      <div className="flex flex-col h-full w-full  mx-auto">
        <Chat initialMessages={messages} tripId={tripId} />
      </div>
    </div>
  )
}