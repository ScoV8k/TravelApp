"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";

export function NavigationMenuDemo() {
  const pathname = usePathname();

  return (
    <NavigationMenu>
      <NavigationMenuList>
        {/* Chat link */}
        <NavigationMenuItem>
          <Link href="/" passHref legacyBehavior>
            <NavigationMenuLink
              className={cn(
                navigationMenuTriggerStyle(),
                pathname === "/" && "bg-accent text-accent-foreground"
              )}
            >
              Chat
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>

        {/* Travel Plan link */}
        <NavigationMenuItem>
          <Link href="/plan" passHref legacyBehavior>
            <NavigationMenuLink
              className={cn(
                navigationMenuTriggerStyle(),
                pathname.startsWith("/plan") && "bg-accent text-accent-foreground"
              )}
            >
              Travel Plan
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>

        {/* Checklists link */}
        <NavigationMenuItem>
          <Link href="/checklists" passHref legacyBehavior>
            <NavigationMenuLink
              className={cn(
                navigationMenuTriggerStyle(),
                pathname.startsWith("/checklists") && "bg-accent text-accent-foreground"
              )}
            >
              Checklists
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>
      </NavigationMenuList>
    </NavigationMenu>
  );
}
