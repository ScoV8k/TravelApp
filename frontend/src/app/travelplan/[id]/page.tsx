"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { Loader2 } from "lucide-react"

type Plan = {
  _id: string
  trip_id: string
  data: Record<string, any>
  updated_at: string
}

export default function PlanPage() {
  const { id } = useParams()
  const planId = id as string

  const [plan, setPlan] = useState<Plan | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPlan = async () => {
      try {
        const res = await fetch(`http://localhost:8000/plans/trip/${planId}`)
        if (!res.ok) throw new Error("Failed to fetch plan")
        const data = await res.json()
        setPlan(data)
      } catch (err) {
        console.error(err)
        setError("Nie udało się pobrać planu.")
      } finally {
        setLoading(false)
      }
    }

    fetchPlan()
  }, [planId])

  return (
    <div className="max-w-4xl mx-auto py-10 px-6">
      <h1 className="text-3xl font-bold mb-6">Plan Podróży</h1>

      {loading && (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="animate-spin w-5 h-5" />
          Ładowanie planu...
        </div>
      )}

      {error && (
        <p className="text-red-500">{error}</p>
      )}

      {plan && (
        <pre className="bg-muted p-4 rounded text-sm overflow-x-auto whitespace-pre-wrap">
          {JSON.stringify(plan.data, null, 2)}
        </pre>
      )}
    </div>
  )
}
