"use client"

import { useState, useEffect } from "react"
import { Loader2 } from "lucide-react"

export function AboutMeModal({
  open,
  onClose,
  userId,
}: {
  open: boolean
  onClose: () => void
  userId: string
}) {
  const [text, setText] = useState("")
  const [isSaving, setIsSaving] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const maxLength = 400

  // Fetchuj zawsze najnowsze about przy otwarciu
  useEffect(() => {
    if (open) {
      const fetchAbout = async () => {
        try {
          setIsLoading(true)
          const res = await fetch(`http://localhost:8000/users/${userId}`)
          if (!res.ok) throw new Error("Failed to fetch user")
          const data = await res.json()
          setText(data.about ?? "")
        } catch (err) {
          console.error("Failed to load about:", err)
          setText("")
        } finally {
          setIsLoading(false)
        }
      }

      fetchAbout()
    }
  }, [open, userId])

  if (!open) return null

  const handleSave = async () => {
    try {
      setIsSaving(true)

      const res = await fetch(`http://localhost:8000/users/${userId}/about`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ about: text }),
      })

      if (!res.ok) {
        throw new Error(`Error: ${res.status}`)
      }

      onClose()
    } catch (err) {
      console.error("Failed to update about:", err)
      alert("Failed to save. Please try again.")
    } finally {
      setIsSaving(false)
    }
  }

  const remainingChars = maxLength - text.length

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm transition-all duration-300"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-xl shadow-xl p-6 w-full max-w-lg transform transition-all duration-300"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Tytuł i opis */}
        <h2 className="text-2xl font-bold mb-1 text-gray-800">
          Write something about yourself
        </h2>
        <p className="text-sm text-gray-500 mb-4">
          Describe yourself in a few words. This description will be taken into
          account when generating the plan.
        </p>

        {/* Label + textarea */}
        <label htmlFor="about-me-text" className="sr-only">
          About me
        </label>
        {isLoading ? (
          <p className="text-gray-500">Loading...</p>
        ) : (
          <>
            <textarea
              id="about-me-text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Write something about yourself..."
              maxLength={maxLength}
              disabled={isSaving}
              className="w-full border border-gray-300 focus:border-blue-500 focus:ring-blue-200 rounded-lg p-4 mb-2 text-gray-800 placeholder-gray-400 outline-none transition-all duration-200 min-h-[120px] resize-none"
            />
            <div className="text-right text-sm text-gray-500 mb-4">
              Characters left: {remainingChars}
            </div>
          </>
        )}

        {/* Przyciski */}
        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            disabled={isSaving}
            className="px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving || isLoading}
            className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white transition-colors disabled:opacity-50 flex items-center"
          >
            {isSaving && (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            )}
            {isSaving ? "Saving..." : "Save changes"}
          </button>
        </div>
      </div>
    </div>
  )
}
