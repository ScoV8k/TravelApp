"use client"

import { CSSProperties, useEffect, useState } from "react"
import { useParams } from "next/navigation"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Progress } from "@/components/ui/progress"
import { PlusCircle, ListTodo, Loader2, Trash2 } from "lucide-react"

interface ChecklistItem {
  id: number
  name: string
  checked: boolean
}

interface Checklist {
  id: number
  name: string
  items: ChecklistItem[]
}

const COLOR_PALETTE = [
  { 
    name: 'blue', 
    title: 'text-blue-600 dark:text-blue-400', 
    hover: 'hover:bg-blue-50 dark:hover:bg-blue-950',
    progressStyle: { '--primary': 'oklch(0.6 0.22 265)' } as CSSProperties,
  },
  { 
    name: 'emerald', 
    title: 'text-emerald-600 dark:text-emerald-400', 
    hover: 'hover:bg-emerald-50 dark:hover:bg-emerald-950',
    progressStyle: { '--primary': 'oklch(0.65 0.18 155)' } as CSSProperties,
  },
  { 
    name: 'amber', 
    title: 'text-amber-600 dark:text-amber-400', 
    hover: 'hover:bg-amber-50 dark:hover:bg-amber-950',
    progressStyle: { '--primary': 'oklch(0.75 0.15 85)' } as CSSProperties,
  },
  { 
    name: 'rose', 
    title: 'text-rose-600 dark:text-rose-400', 
    hover: 'hover:bg-rose-50 dark:hover:bg-rose-950',
    progressStyle: { '--primary': 'oklch(0.65 0.2 15)' } as CSSProperties,
  },
  { 
    name: 'violet', 
    title: 'text-violet-600 dark:text-violet-400', 
    hover: 'hover:bg-violet-50 dark:hover:bg-violet-950',
    progressStyle: { '--primary': 'oklch(0.65 0.2 285)' } as CSSProperties,
  },
];


export default function ChecklistPage() {
  const { id } = useParams()
  const tripId = id as string

  const [checklists, setChecklists] = useState<Checklist[]>([])
  const [newChecklistName, setNewChecklistName] = useState("")
  const [newItemText, setNewItemText] = useState<{ [key: number]: string }>({})
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)

  useEffect(() => {
    async function fetchChecklists() {
      setIsLoading(true)
      try {
        const res = await fetch(`http://localhost:8000/information/trip/${tripId}/checklists`)
        if (!res.ok) throw new Error("Failed to load checklists")
        const data: Checklist[] = await res.json()
        setChecklists(data)
      } catch (e) {
        console.error(e)
      } finally {
        setIsLoading(false)
      }
    }
    if (tripId) fetchChecklists()
  }, [tripId])

  const performApiAction = async (
    action: () => Promise<void>,
    optimisticUpdate?: () => void,
    rollback?: () => void
  ) => {
    if (optimisticUpdate) optimisticUpdate();
    setIsSaving(true)
    try {
      await action()
    } catch (e) {
      console.error(e)
      if (rollback) rollback();
    } finally {
      setIsSaving(false)
    }
  }

  const addChecklist = (name: string) => {
    performApiAction(async () => {
      const res = await fetch(`http://localhost:8000/information/trip/${tripId}/checklists/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      })
      if (!res.ok) throw new Error("Failed to add checklist")
      const updated: Checklist[] = await res.json()
      setChecklists(updated)
      setNewChecklistName("")
    })
  }

  const addItem = (checklistId: number, name: string) => {
    performApiAction(async () => {
      const res = await fetch(`http://localhost:8000/information/trip/${tripId}/checklists/${checklistId}/items/add`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name }),
      })
      if (!res.ok) throw new Error("Failed to add item")
      const updated: Checklist[] = await res.json()
      setChecklists(updated)
      setNewItemText(prev => ({ ...prev, [checklistId]: "" }))
    })
  }

  const toggleItem = (checklistId: number, itemId: number, checked: boolean) => {
    const originalChecklists = checklists
    const optimisticUpdate = () => setChecklists(prev => prev.map(cl => 
      cl.id === checklistId 
        ? { ...cl, items: cl.items.map(it => it.id === itemId ? { ...it, checked } : it) }
        : cl
    ))
    const rollback = () => setChecklists(originalChecklists)

    performApiAction(async () => {
      const res = await fetch(`http://localhost:8000/information/trip/${tripId}/checklists/${checklistId}/items/${itemId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(checked),
      })
      if (!res.ok) throw new Error("Failed to toggle item")
      const updated: Checklist[] = await res.json()
      setChecklists(updated)
    }, optimisticUpdate, rollback)
  }

  const deleteChecklist = (checklistId: number) => {
    if (!window.confirm("Are you sure you want to delete this list and all its items?")) {
      return
    }

    const originalChecklists = checklists
    const optimisticUpdate = () => setChecklists(prev => prev.filter(cl => cl.id !== checklistId))
    const rollback = () => setChecklists(originalChecklists)

    performApiAction(async () => {
      const res = await fetch(`http://localhost:8000/information/trip/${tripId}/checklists/${checklistId}`, {
        method: "DELETE",
      })
      if (!res.ok) throw new Error("Failed to delete checklist")
      const updated: Checklist[] = await res.json()
      setChecklists(updated)
    }, optimisticUpdate, rollback)
  }

  const deleteItem = (checklistId: number, itemId: number) => {
    const originalChecklists = checklists
    const optimisticUpdate = () => setChecklists(prev => prev.map(cl => 
      cl.id === checklistId ? { ...cl, items: cl.items.filter(it => it.id !== itemId) } : cl
    ))
    const rollback = () => setChecklists(originalChecklists)

    performApiAction(async () => {
      const res = await fetch(`http://localhost:8000/information/trip/${tripId}/checklists/${checklistId}/items/${itemId}`, {
        method: "DELETE",
      })
      if (!res.ok) throw new Error("Failed to delete item")
      const updated: Checklist[] = await res.json()
      setChecklists(updated)
    }, optimisticUpdate, rollback)
  }

  const handleAddChecklist = () => {
    if (newChecklistName.trim()) {
      addChecklist(newChecklistName.trim())
    }
  }
  
  const handleAddItem = (checklistId: number) => {
    if (newItemText[checklistId]?.trim()) {
      addItem(checklistId, newItemText[checklistId].trim())
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 sm:px-6">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Checklists</h1>
      </div>

      <div className="pb-8 mb-8 border-b">
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <Input
            placeholder="e.g. Packing list, Documents..."
            value={newChecklistName}
            onChange={(e) => setNewChecklistName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAddChecklist()}
            disabled={isSaving}
            className="flex-grow"
          />
          <Button
            onClick={handleAddChecklist}
            disabled={isSaving || !newChecklistName.trim()}
            className="w-full sm:w-auto"
          >
            {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <PlusCircle className="mr-2 h-4 w-4" />}
            Add new list
          </Button>
        </div>
      </div>
      
      {checklists.length > 0 ? (
        <div className="space-y-16">
          {checklists.map((cl, index) => {
            const totalItems = cl.items.length
            const completedItems = cl.items.filter((item) => item.checked).length
            const progress = totalItems > 0 ? (completedItems / totalItems) * 100 : 0
            const theme = COLOR_PALETTE[index % COLOR_PALETTE.length];

            return (
              <section key={cl.id} className="space-y-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className={`text-2xl font-semibold ${theme.title}`}>{cl.name}</h2>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      Completed {completedItems} of {totalItems}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => deleteChecklist(cl.id)}
                    disabled={isSaving}
                    aria-label="Delete list"
                  >
                    <Trash2 className="h-4 w-4 text-muted-foreground hover:text-red-500 transition-colors" />
                  </Button>
                </div>
                <Progress value={progress} className="mt-2" style={theme.progressStyle} />

                <div className="space-y-2 pt-4">
                  {cl.items.map((item) => (
                    <div key={item.id} className={`group flex items-center gap-3 p-2 rounded-md transition-colors ${theme.hover}`}>
                      <Checkbox
                        id={`item-${item.id}`}
                        checked={item.checked}
                        onCheckedChange={(checked) => toggleItem(cl.id, item.id, !!checked)}
                        disabled={isSaving}
                      />
                      <label
                        htmlFor={`item-${item.id}`}
                        className={`flex-grow cursor-pointer text-sm font-medium transition-colors ${item.checked ? "line-through text-muted-foreground" : "text-slate-700 dark:text-slate-300"}`}
                      >
                        {item.name}
                      </label>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => deleteItem(cl.id, item.id)}
                        disabled={isSaving}
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                        aria-label="Delete item"
                      >
                        <Trash2 className="h-4 w-4 text-muted-foreground hover:text-red-500 transition-colors" />
                      </Button>
                    </div>
                  ))}
                </div>

                <div className="flex items-center gap-2 mt-4 pt-4 border-t">
                  <Input
                    placeholder="Add new item..."
                    value={newItemText[cl.id] || ""}
                    onChange={(e) => setNewItemText({ ...newItemText, [cl.id]: e.target.value })}
                    onKeyDown={(e) => e.key === "Enter" && handleAddItem(cl.id)}
                    disabled={isSaving}
                  />
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleAddItem(cl.id)}
                    disabled={isSaving || !(newItemText[cl.id]?.trim())}
                  >
                    Add
                  </Button>
                </div>
              </section>
            )
          })}
        </div>
      ) : (
        <div className="text-center py-16 border-2 border-dashed rounded-lg">
          <ListTodo className="mx-auto h-12 w-12 text-muted-foreground" />
          <h3 className="mt-4 text-lg font-semibold">You don't have any checklists yet</h3>
          <p className="mt-1 text-sm text-muted-foreground">
            Add your first list to start organizing your trip.
          </p>
        </div>
      )}
    </div>
  )
}