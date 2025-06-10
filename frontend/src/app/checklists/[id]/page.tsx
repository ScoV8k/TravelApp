"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"

interface ChecklistItem {
  id: number
  name: string
  checked: boolean
}

export default function ChecklistPage() {
  const { id } = useParams()
  const tripId = id as string

  const [items, setItems] = useState<ChecklistItem[]>([])
  const [newItemText, setNewItemText] = useState("")
  const [isSaving, setIsSaving] = useState(false)

  // --- Pobierz checklistę z backendu przy starcie ---
  useEffect(() => {
    async function fetchChecklist() {
      try {
        const res = await fetch(`http://localhost:8000/information/trip/${tripId}/checklist`)
        if (!res.ok) throw new Error("Failed to load checklist")
        const data: ChecklistItem[] = await res.json()
        setItems(data)
      } catch (e) {
        console.error(e)
      }
    }
    if (tripId) fetchChecklist()
  }, [tripId])

  // --- Dodaj nowy element do checklisty ---
  async function addItem(name: string) {
    setIsSaving(true)
    try {
      const res = await fetch(`http://localhost:8000/information/trip/${tripId}/checklist/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      })
      if (!res.ok) throw new Error("Failed to add checklist item")
      const updatedChecklist: ChecklistItem[] = await res.json()
      setItems(updatedChecklist)
    } catch (e) {
      console.error(e)
    } finally {
      setIsSaving(false)
    }
  }

  // --- Toggle checked dla pojedynczego elementu ---
  async function toggleItemChecked(id: number, checked: boolean) {
    setIsSaving(true)
    try {
      const res = await fetch(`http://localhost:8000/information/trip/${tripId}/checklist/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(checked),
      })
      if (!res.ok) throw new Error("Failed to update checklist item")

      const updatedChecklist: ChecklistItem[] = await res.json()
      setItems(updatedChecklist)
    } catch (e) {
      console.error(e)
    } finally {
      setIsSaving(false)
    }
  }

  // Handler dodawania
  const handleAddItem = () => {
    if (!newItemText.trim()) return
    addItem(newItemText.trim())
    setNewItemText("")
  }

  // Handler toggle
  const handleToggle = (id: number, currentChecked: boolean) => {
    toggleItemChecked(id, !currentChecked)
  }

  return (
    <div className="max-w-xl mx-auto py-10 px-6">
      <h1 className="text-3xl font-bold mb-6">Checklist</h1>

      <div className="flex items-center gap-2 mb-6">
        <Input
          placeholder="Add new item"
          value={newItemText}
          onChange={(e) => setNewItemText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault()
              handleAddItem()
            }
          }}
          disabled={isSaving}
        />
        <Button onClick={handleAddItem} disabled={isSaving || !newItemText.trim()}>
          {isSaving ? "Saving..." : "Add"}
        </Button>
      </div>

      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.id} className="flex items-center gap-2">
            <Checkbox
              id={`item-${item.id}`}
              checked={item.checked}
              onCheckedChange={() => handleToggle(item.id, item.checked)}
              disabled={isSaving}
            />
            <label
              htmlFor={`item-${item.id}`}
              className={`text-base ${item.checked ? "line-through text-muted-foreground" : ""}`}
            >
              {item.name}
            </label>
          </div>
        ))}
      </div>
    </div>
  )
}
