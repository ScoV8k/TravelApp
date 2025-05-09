"use client";

import "./globals.css";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/app-sidebar";
import { NavigationMenuDemo } from "@/components/navigation-menu";
import { usePathname } from "next/navigation";
import { TripProvider } from "./context/TripContext";

export default function Layout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLoginPage = pathname === "/login";
  return (
    <html lang="en">
      <body className="overflow-hidden">
        <SidebarProvider>
          <TripProvider>
            {!isLoginPage && <AppSidebar />}
            {!isLoginPage ? (
              <main className="flex flex-col w-full h-screen">
                <div className="flex items-center p-4 border-b">
                  <SidebarTrigger />
                  <NavigationMenuDemo />
                </div>
                <div className="flex-1 overflow-y-auto">
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
  )
}