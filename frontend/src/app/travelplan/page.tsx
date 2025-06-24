import { NavigationMenu } from "@radix-ui/react-navigation-menu";
import { Chat } from "@/components/chat";

export default function TravelPlan() {
  return (
    <div className="w-full">
    <div>
  <NavigationMenu></NavigationMenu>
</div>
<div className="flex flex-col h-full w-full max-w-2xl mx-auto">

    <Chat />
  </div>
  </div>
  );
}