"use client"

import { useRouter } from "next/navigation"
import { Chat } from "@/components/chat"

export default function Home() {
  const router = useRouter()

  return (
    <div className="flex flex-col h-full w-full">
      <div className="flex flex-col h-full w-full max-w-4xl mx-auto px-2 md:px-4 pt-4 md:pt-10">
        <Chat />
      </div>
    </div>
  )
}
