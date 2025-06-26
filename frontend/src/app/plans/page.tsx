"use client"

import { useEffect, useState } from "react"
import Link from "next/link"

type Plan = {
  id: string
  trip_name: string
}

export default function PlansPage() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchPlans() {
      try {
        const res = await fetch("http://localhost:8000/plans/all-names") // zmień na produkcyjny URL jeśli trzeba
        if (!res.ok) throw new Error("Failed to fetch plans")
        const data = await res.json()
        setPlans(data)
      } catch (err: any) {
        setError(err.message || "Unknown error")
      } finally {
        setLoading(false)
      }
    }

    fetchPlans()
  }, [])

  if (loading) return <div className="p-4">Loading plans...</div>
  if (error) return <div className="p-4 text-red-500">Error: {error}</div>

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">All Travel Plans</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {plans.map((plan) => (
          <Link
            key={plan.id}
            href={`/plan/${plan.id}`}
            className="p-4 rounded-xl border border-gray-300 hover:shadow-md transition bg-white"
          >
            <h2 className="text-lg font-semibold">{plan.trip_name}</h2>
            <p className="text-sm text-gray-500 mt-1">View Details →</p>
          </Link>
        ))}
      </div>
    </main>
  )
}
