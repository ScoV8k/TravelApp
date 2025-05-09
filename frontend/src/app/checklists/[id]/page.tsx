"use client"

import { useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"

interface ChecklistItem {
  id: string
  text: string
  checked: boolean
}

export default function ChecklistPage() {
  const { id } = useParams()
  const tripId = id as string

  const [items, setItems] = useState<ChecklistItem[]>([])
  const [newItemText, setNewItemText] = useState("")

  const handleAddItem = () => {
    if (!newItemText.trim()) return

    const newItem: ChecklistItem = {
      id: crypto.randomUUID(),
      text: newItemText.trim(),
      checked: false,
    }

    setItems((prev) => [...prev, newItem])
    setNewItemText("")
  }

  const toggleItem = (id: string) => {
    setItems((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, checked: !item.checked } : item
      )
    )
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
        />
        <Button onClick={handleAddItem}>Add</Button>
      </div>

      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.id} className="flex items-center gap-2">
            <Checkbox
              id={`item-${item.id}`}
              checked={item.checked}
              onCheckedChange={() => toggleItem(item.id)}
            />
            <label
              htmlFor={`item-${item.id}`}
              className={`text-base ${item.checked ? "line-through text-muted-foreground" : ""}`}
            >
              {item.text}
            </label>
          </div>
        ))}
      </div>
    </div>
  )
}
