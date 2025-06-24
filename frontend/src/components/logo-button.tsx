"use client";

import * as React from "react";
import { SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar";

export function LogoButton() {
  return (
    <SidebarMenu>
      <SidebarMenuItem>
        <SidebarMenuButton size="lg" className="flex items-center">
          <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-sidebar-primary " >
            <img
              src="/logo.png"
              alt="Logo"
              className="w-full h-full object-cover"
            />
          </div>
          <div className="grid flex-1 text-left leading-tight">
            <span className="truncate font-semibold text-sm">TraveLio</span>
            <span className="truncate text-xs text-muted-foreground">Planning App</span>
          </div>
        </SidebarMenuButton>
      </SidebarMenuItem>
    </SidebarMenu>
  );
}
