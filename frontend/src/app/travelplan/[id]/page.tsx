"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import {
  MapPin,
  Users,
  CalendarDays,
  Hotel,
  Landmark,
  Wallet,
  StickyNote,
  Activity,
} from "lucide-react"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"

interface TravelInformation {
  destination_countries: string[]
  destination_cities: string[]
  start_date: string | null
  end_date: string | null
  duration_days: number | null
  travelers_details: {
    name: string | null
    age: number | null
    preferences: string | null
  }[]
  accommodation: {
    city: string | null
    check_in: string | null
    check_out: string | null
    chosen_hotel: string | null
  }[]
  places_to_visit: {
    city: string | null
    duration_days: number | null
    activities: {
      name: string | null
      type: string | null
      description: string | null
      location: string | null
    }[]
  }[]
  budget: {
    estimated_total: number | null
    categories: {
      transport: number | null
      accommodation: number | null
      food: number | null
      activities: number | null
    }
    currency: string | null
  }
  additional_notes: {
    text: string | null
  }[]
}

type TripPlanResponse = {
  _id: string
  trip_id: string
  data: TravelInformation
  updated_at: string
}

function PlanSkeleton() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-1 space-y-8">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-5 w-full" />
            <Skeleton className="h-5 w-5/6" />
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-3/4" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-5 w-full" />
            <Skeleton className="h-5 w-full" />
          </CardContent>
        </Card>
      </div>
      <div className="lg:col-span-2 space-y-8">
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-1/2" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default function PlanPage() {
  const { id } = useParams()
  const planId = id as string

  const [plan, setPlan] = useState<TripPlanResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!planId) return
    const fetchPlan = async () => {
      setLoading(true)
      try {
        const res = await fetch(`http://localhost:8000/information/trip/${planId}`)
        if (!res.ok) {
          throw new Error(`Failed to fetch plan (status: ${res.status})`)
        }
        const data = await res.json()
        setPlan(data)
      } catch (err: any) {
        console.error(err)
        setError(err.message || "An unknown error occurred.")
      } finally {
        setLoading(false)
      }
    }
    fetchPlan()
  }, [planId])

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto py-10 px-4 sm:px-6">
        <h1 className="text-3xl font-bold mb-8">Your Trip Plan</h1>
        <PlanSkeleton />
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto py-10 px-4 sm:px-6">
        <h1 className="text-3xl font-bold mb-8">An Error Occurred</h1>
        <Alert variant="destructive">
          <AlertTitle>Failed to Load Plan</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    )
  }

  const travelInfo = plan?.data

  return (
    <div className="max-w-6xl mx-auto py-10 px-4 sm:px-6">
      <h1 className="text-3xl font-bold mb-8">Your Trip Plan</h1>

      {travelInfo && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* --- Kolumna boczna --- */}
          <aside className="lg:col-span-1 space-y-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="w-5 h-5" />
                  Destination
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {travelInfo.destination_countries && travelInfo.destination_countries.length > 0 && (
                  <p className="text-sm">
                    <strong>Countries:</strong> {travelInfo.destination_countries.join(", ")}
                  </p>
                )}
                {travelInfo.destination_cities && travelInfo.destination_cities.length > 0 && (
                  <div>
                    <strong className="text-sm">Cities:</strong>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {travelInfo.destination_cities.map((city) => (
                        <Badge key={city} variant="secondary">{city}</Badge>
                      ))}
                    </div>
                  </div>
                )}
                {travelInfo.start_date && travelInfo.end_date && (
                  <div className="flex items-center gap-2 text-sm text-muted-foreground pt-2">
                    <CalendarDays className="w-4 h-4" />
                    <span>{travelInfo.start_date} – {travelInfo.end_date} ({travelInfo.duration_days} days)</span>
                  </div>
                )}
              </CardContent>
            </Card>

            {travelInfo.travelers_details && travelInfo.travelers_details.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Travelers
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {travelInfo.travelers_details.map((t, idx) => (
                    t.name && (
                      <li key={idx} className="text-sm">
                        <strong>{t.name}</strong>
                        {t.age !== null && `, ${t.age} yrs`}
                        {t.preferences && <p className="text-xs text-muted-foreground">{t.preferences}</p>}
                      </li>
                    )
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}


            {travelInfo.budget?.estimated_total && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Wallet className="w-5 h-5" />
                    Budget
                  </CardTitle>
                  <CardDescription>
                    Total: <strong className="text-foreground">{travelInfo.budget.estimated_total} {travelInfo.budget.currency}</strong>
                  </CardDescription>
                </CardHeader>
                {travelInfo.budget.categories && (
                  <CardContent>
                    <ul className="space-y-1 text-sm">
                      {Object.entries(travelInfo.budget.categories).map(([cat, val]) => (
                        val && (
                            <li key={cat} className="flex justify-between">
                              <span className="capitalize text-muted-foreground">{cat}</span>
                              <span>{val} {travelInfo.budget.currency}</span>
                            </li>
                        )
                      ))}
                    </ul>
                  </CardContent>
                )}
              </Card>
            )}
          </aside>

          <main className="lg:col-span-2 space-y-8">
            {travelInfo.accommodation && travelInfo.accommodation.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Hotel className="w-5 h-5" />
                    Accommodation
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {travelInfo.accommodation.map((a, idx) => (
                    a.city && (
                      <div key={idx} className="p-3 bg-muted/50 rounded-lg">
                        <div className="flex justify-between font-semibold">
                          <span>{a.city}</span>
                          <span className="text-sm font-normal text-muted-foreground">{a.check_in} to {a.check_out}</span>
                        </div>
                        {a.chosen_hotel && <p className="text-sm mt-1">✓ Chosen: {a.chosen_hotel}</p>}
                      </div>
                    )
                  ))}
                </CardContent>
              </Card>
            )}

            {travelInfo.places_to_visit && travelInfo.places_to_visit.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Landmark className="w-5 h-5" />
                    Itinerary & Activities
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Accordion type="single" collapsible className="w-full">
                    {travelInfo.places_to_visit.map((place, idx) => (
                      place.city && (
                        <AccordionItem value={`city-${idx}`} key={idx}>
                          <AccordionTrigger>
                            <div className="flex justify-between w-full pr-4">
                                <span>{place.city}</span>
                                {place.duration_days && <span className="text-sm text-muted-foreground font-normal">{place.duration_days} days</span>}
                            </div>
                          </AccordionTrigger>
                          <AccordionContent className="space-y-4 pt-4">
                            {place.activities && place.activities.length > 0 ? (
                              place.activities.map((activity, actIdx) => (
                                <div key={actIdx} className="p-3 border rounded-md text-sm">
                                  <div className="flex justify-between items-start">
                                    <strong className="font-semibold">{activity.name}</strong>
                                    {activity.type && <Badge variant="outline">{activity.type}</Badge>}
                                  </div>
                                  {activity.description && <p className="text-muted-foreground mt-1">{activity.description}</p>}
                                  {activity.location && (
                                    <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                                      <MapPin className="w-3 h-3"/>
                                      <span>{activity.location}</span>
                                    </div>
                                  )}
                                </div>
                              ))
                            ) : (
                              <p className="text-sm text-muted-foreground">No activities planned for this city.</p>
                            )}
                          </AccordionContent>
                        </AccordionItem>
                      )
                    ))}
                  </Accordion>
                </CardContent>
              </Card>
            )}


            {travelInfo.additional_notes && travelInfo.additional_notes.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <StickyNote className="w-5 h-5" />
                    Additional Notes
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="list-disc pl-5 space-y-1 text-sm">
                    {travelInfo.additional_notes.map((note, idx) => (
                      note.text && <li key={idx}>{note.text}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </main>
        </div>
      )}
    </div>
  )
}