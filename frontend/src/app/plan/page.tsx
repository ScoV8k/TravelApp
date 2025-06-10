import { ChatBotUi } from "@/components/chatbotUI-old";
import { NavigationMenu } from "@radix-ui/react-navigation-menu";
import Image from "next/image";
import { Chat } from "@/components/chat";

export default function TravelPlan() {
  return (
    <div className="w-full">
    <div>
  {/* <h1 className="text-2xl font-bold">Mój projekt z Tailwind CSS</h1>
  <p className="mt-4">Next.js + Tailwind CSS działa poprawnie!</p> */}
  <NavigationMenu></NavigationMenu>
  {/* <ChatBotUi></ChatBotUi> */}
</div>
<div className="flex flex-col h-full w-full max-w-2xl mx-auto">

    <Chat />
  </div>
  </div>
  );
}