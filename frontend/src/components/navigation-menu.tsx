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

  // fallback: jeśli nie mamy tripId w kontekście, wyciągamy je z pathname
  const tripIdMatch = pathname.match(/(?:\/trip|\/travelplan|\/checklists)\/([^/]+)/)
  const tripId = contextTripId || (tripIdMatch ? tripIdMatch[1] : null)
  

  return (
    <NavigationMenu>
      <NavigationMenuList>
        {/* Chat */}
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

        {/* Travel Plan */}
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
              Travel Plan
            </NavigationMenuLink>
          </Link>
        </NavigationMenuItem>

        {/* Checklists */}
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

        {/* Nazwa tripa */}
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
