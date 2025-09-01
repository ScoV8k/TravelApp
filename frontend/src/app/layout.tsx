"use client";

import "./globals.css";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { NavigationMenuDemo } from "@/components/navigation-menu";
import { usePathname } from "next/navigation";
import { TripProvider } from "./context/TripContext";
import { useAuthRedirect } from "@/hooks/useAuthRedirect";

export default function Layout({ children }: { children: React.ReactNode }) {
  useAuthRedirect();
  const pathname = usePathname();
  const isAuthPage = pathname === "/login" || pathname === "/register";

  return (
    <html lang="pl">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
      </head>
      <body className="overflow-hidden md:overflow-hidden">
        <SidebarProvider>
          <TripProvider>
            {!isAuthPage && <AppSidebar />}
            {!isAuthPage ? (
              <main className="flex flex-col w-full h-screen md:h-screen">
                <div className="flex items-center p-2 md:p-4 border-b">
                  <SidebarTrigger />
                  <NavigationMenuDemo />
                </div>
                <div className="flex-1 overflow-y-auto w-full">
                  {children}
                </div>
              </main>
            ) : (
              <main className="w-full min-h-screen">{children}</main>
            )}
          </TripProvider>
        </SidebarProvider>
      </body>
    </html>
  );
}