"use client"
import { createContext, useContext, useState, ReactNode } from "react"

type TripContextType = {
    tripName: string
    setTripName: (name: string) => void
    tripId: string | null
    setTripId: (id: string | null) => void
  }
  
  const TripContext = createContext<TripContextType | undefined>(undefined)
  
  export function TripProvider({ children }: { children: React.ReactNode }) {
    const [tripName, setTripName] = useState("")
    const [tripId, setTripId] = useState<string | null>(null)
  
    return (
      <TripContext.Provider value={{ tripName, setTripName, tripId, setTripId }}>
        {children}
      </TripContext.Provider>
    )
  }
  

export function useTrip() {
  const context = useContext(TripContext)
  if (!context) throw new Error("useTrip must be used within TripProvider")
  return context
}
