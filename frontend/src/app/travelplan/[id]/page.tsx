"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { Loader2 } from "lucide-react"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

interface ChecklistItem {
  id: number
  name: string
  checked: boolean
}

type Plan = {
  _id: string
  trip_id: string
  data: Record<string, any>
  updated_at: string
  checklist: ChecklistItem[]
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
        const res = await fetch(`http://localhost:8000/information/trip/${planId}`)
        if (!res.ok) throw new Error("Failed to fetch plan")
        const data = await res.json()
        setPlan(data)
      } catch (err) {
        console.error(err)
        setError("Failed to fetch the plan.") // Translated
      } finally {
        setLoading(false)
      }
    }

    fetchPlan()
  }, [planId])

  const data = plan?.data

  return (
    <div className="max-w-4xl mx-auto py-10 px-6">
      <h1 className="text-3xl font-bold mb-6">Trip Plan</h1> {/* Added a title */}

      {loading && (
        <div className="flex items-center gap-2 text-muted-foreground">
          <Loader2 className="animate-spin w-5 h-5" />
          Plan loading...
        </div>
      )}

      {error && <p className="text-red-500">{error}</p>}

      {data && (
        <div className="space-y-6">
          {(data.destination_country || data.destination_cities?.length || data.start_date) && (
            <section>
              <h2 className="text-xl font-semibold">📍 Destination</h2> 
              {data.destination_country && <p><strong>Country:</strong> {data.destination_country}</p>} 
              {data.destination_cities?.length > 0 && <p><strong>Cities:</strong> {data.destination_cities.join(", ")}</p>} 
              {data.start_date && data.end_date && data.duration_days && (
                <p><strong>Dates:</strong> {data.start_date} – {data.end_date} ({data.duration_days} days)</p> 
              )}
            </section>
          )}

          {data.travelers_details?.length > 0 && (
            <section>
              <h2 className="text-xl font-semibold">🧍‍♂️ Travelers</h2> 
              {data.travelers_details.map((traveler: any, idx: number) => (
                <p key={idx}>👤 {traveler.name} ({traveler.age} years old) – {traveler.preferences}</p>
              ))}
            </section>
          )}

          {data.accommodation?.length > 0 && (
            <section>
              <h2 className="text-xl font-semibold">🏨 Accommodation</h2> 
              {data.accommodation.map((a: any, idx: number) => (
                <div key={idx} className="mb-2">
                  <p><strong>{a.city}</strong>: {a.check_in} – {a.check_out}</p>
                  {a.chosen_hotel && <p>Chosen hotel: {a.chosen_hotel}</p>} 
                  {a.suggested_hotels?.length > 0 && <p>Other suggestions: {a.suggested_hotels.join(", ")}</p>} 
                </div>
              ))}
            </section>
          )}

          {data.places_to_visit?.length > 0 && (
            <section>
              <h2 className="text-xl font-semibold">📌 Attractions</h2> 
              <Accordion type="single" collapsible>
                {data.places_to_visit.map((place: any, idx: number) => (
                  <AccordionItem value={`day-${idx}`} key={idx}>
                    <AccordionTrigger>{place.city}</AccordionTrigger>
                    <AccordionContent>
                      {place.user_selected?.length > 0 && (
                        <p><strong>Selected:</strong> {place.user_selected.join(", ")}</p> // 
                      )}
                      {place.suggested_places?.length > 0 && (
                        <p><strong>Suggestions:</strong> {place.suggested_places.join(", ")}</p> // 
                      )}
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            </section>
          )}

          {data.activities?.length > 0 && (
            <section>
              <h2 className="text-xl font-semibold">🎭 Activities</h2> 
              {data.activities.map((a: any, idx: number) => (
                <div key={idx} className="mb-2">
                  <p><strong>{a.type}</strong>: {a.description} ({a.location})</p>
                  {a.suggested_options?.length > 0 && <p>Suggestions: {a.suggested_options.join(", ")}</p>} 
                </div>
              ))}
            </section>
          )}

          {data.budget && (
            <section>
              <h2 className="text-xl font-semibold">💰 Budget</h2> 
              {data.budget.estimated_total && data.budget.currency && (
                <p><strong>Total:</strong> {data.budget.estimated_total} {data.budget.currency}</p> // 
              )}
              {data.budget.categories && (
                <ul className="list-disc ml-6">
                  {Object.entries(data.budget.categories).map(([category, value]) => (
                    <li key={category}>{category}: {value} {data.budget.currency}</li>
                  ))}
                </ul>
              )}
            </section>
          )}

          {data.additional_notes?.length > 0 && (
            <section>
              <h2 className="text-xl font-semibold">📝 Notes</h2> 
              <ul className="list-disc ml-6">
                {data.additional_notes.map((note: any, idx: number) => (
                  <li key={idx}>{note.text}</li>
                ))}
              </ul>
            </section>
          )}
        </div>
      )}
    </div>
  )
}