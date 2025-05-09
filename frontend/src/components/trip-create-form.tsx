import { useState } from "react"
import { useRouter } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

type TripCreateFormProps = {
    onCancel: () => void
    onTripCreated: (trip: { _id: string; name: string }) => void
  }
  
  export function TripCreateForm({ onCancel, onTripCreated }: TripCreateFormProps) {
    const [name, setName] = useState("")
    const router = useRouter()
  
    const createTrip = async () => {
      const token = localStorage.getItem("token")
      const userId = localStorage.getItem("user_id")
      if (!token || !userId || !name.trim()) return
  
      try {
        const res = await fetch("http://localhost:8000/trips/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            user_id: userId,
            name: name.trim(),
            status: "draft",
            created_at: new Date().toISOString(),
            plan: {},
          }),
        })
  
        if (!res.ok) throw new Error("Błąd podczas tworzenia podróży")
  
        const newTrip = await res.json()
        onTripCreated(newTrip)
        onCancel()
  
        // ⏱️ małe opóźnienie, by React zdążył zrenderować nowy trip
        setTimeout(() => {
          router.push(`/trip/${newTrip._id}`)
        }, 100)
      } catch (err) {
        console.error("Nie udało się stworzyć podróży:", err)
      }
    }

    
  return (
    <div className="flex flex-col gap-2 w-full">
      <Input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Trip name"
        className="text-sm"
      />
      <div className="flex gap-2">
        <Button
          onClick={createTrip}
          className="flex-1 text-sm border "
          variant="ghost" // bardziej widoczny, ale nie krzykliwy
        >
          Utwórz
        </Button>
        <Button
          onClick={onCancel}
          className="flex-1 text-sm text-muted-foreground"
          variant="ghost" // lekki, subtelny
        >
          Anuluj
        </Button>
      </div>
    </div>
  )
}
