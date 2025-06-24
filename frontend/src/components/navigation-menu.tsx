"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"

import { cn } from "@/lib/utils"
import {
  NavigationMenu,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu"

import { useTrip } from "@/app/context/TripContext"

export function NavigationMenuDemo() {
  const pathname = usePathname()
  const { tripName, tripId: contextTripId } = useTrip()
  const tripIdMatch = pathname.match(/(?:\/trip|\/travelplan|\/checklists)\/([^/]+)/)
  const tripId = contextTripId || (tripIdMatch ? tripIdMatch[1] : null)
  

  return (
    <NavigationMenu>
      <NavigationMenuList>
        <NavigationMenuItem>
          <Link
            href={tripId ? `/trip/${tripId}` : "/"}
            passHref
            legacyBehavior
          >
            <NavigationMenuLink
              className={cn(
                navigationMenuTriggerStyle(),
                (pathname === "/" || pathname.startsWith("/trip/")) &&
                  !pathname.includes("travelplan") &&
                  !pathname.includes("checklists") &&
                  "bg-accent text-accent-foreground"
              )}
            >
              Chat
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>

        <NavigationMenuItem>
          <Link
            href={tripId ? `/travelplan/${tripId}` : "/travelplan"}
            passHref
            legacyBehavior
          >
            <NavigationMenuLink
              className={cn(
                navigationMenuTriggerStyle(),
                pathname.startsWith("/travelplan") && "bg-accent text-accent-foreground"
              )}
            >
              Travel Information
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>

        <NavigationMenuItem>
          <Link
            href={tripId ? `/checklists/${tripId}` : "/checklists"}
            passHref
            legacyBehavior
          >
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

        <NavigationMenuItem>
          <Link
            href={tripId ? `/plan/${tripId}` : "/plan"}
            passHref
            legacyBehavior
          >
            <NavigationMenuLink
              className={cn(
                navigationMenuTriggerStyle(),
                pathname.startsWith("/plan") && "bg-accent text-accent-foreground"
              )}
            >
              Plan
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>

        {tripId && tripName && (
          <NavigationMenuItem>
            <span
              className={cn(
                navigationMenuTriggerStyle(),
                "text-muted-foreground cursor-default pointer-events-none"
              )}
            >
              {tripName}
            </span>
          </NavigationMenuItem>
        )}
      </NavigationMenuList>
    </NavigationMenu>
  )
}
