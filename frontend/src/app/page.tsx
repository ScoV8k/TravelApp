"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ChatBotUi } from "@/components/chatbotUI-old";
import { NavigationMenu } from "@radix-ui/react-navigation-menu";
import { Chat } from "@/components/chat";

export default function Home() {
  // const [authorized, setAuthorized] = useState(false);
  const router = useRouter();

  return (
    <div className="w-full">
      <div className="bg-blue-500 text-white p-6 rounded-lg shadow-lg">
        <h1 className="text-2xl font-bold">Mój projekt z Tailwind CSS</h1>
        <p className="mt-4">Next.js + Tailwind CSS działa poprawnie!</p>
        <NavigationMenu />
        {/* <ChatBotUi /> */}
      </div>
      <div className="flex flex-col h-full w-full max-w-2xl mx-auto">
        <Chat />
      </div>
    </div>
  );
}
