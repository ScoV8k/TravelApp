"use client"

import {
  SidebarMenu,
  SidebarGroup,
  SidebarMenuItem,
  SidebarMenuButton,
} from "@/components/ui/sidebar"

import Link from "next/link"

import * as React from "react"
import {
  AudioWaveform,
  Command,
  Flag,
  GalleryVerticalEnd,
  SquareTerminal,
  Plus,
} from "lucide-react"

import { type LucideIcon } from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavTravels } from "@/components/nav-travels"
import { NavUser } from "@/components/nav-user"
import { useRouter } from "next/navigation"
import { useState, useEffect } from "react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"
import { LogoButton } from "./logo-button"
import { TripCreateForm } from "@/components/trip-create-form"

const data = {

  teams: [
    {
      name: "Acme Inc",
      logo: GalleryVerticalEnd,
      plan: "Enterprise",
    },
    {
      name: "Acme Corp.",
      logo: AudioWaveform,
      plan: "Startup",
    },
    {
      name: "Evil Corp.",
      logo: Command,
      plan: "Free",
    },
  ],
  navMain: [
    {
      title: "Your Plans",
      url: "#",
      icon: SquareTerminal,
      isActive: false,
      items: [
        {
          title: "History",
          url: "#",
        },
        {
          title: "Starred",
          url: "#",
        },
        {
          title: "Settings",
          url: "#",
        },
      ],
    },
  //   {
  //     title: "Models",
  //     url: "#",
  //     icon: Bot,
  //     items: [
  //       {
  //         title: "Genesis",
  //         url: "#",
  //       },
  //       {
  //         title: "Explorer",
  //         url: "#",
  //       },
  //       {
  //         title: "Quantum",
  //         url: "#",
  //       },
  //     ],
  //   },
  //   {
  //     title: "Documentation",
  //     url: "#",
  //     icon: BookOpen,
  //     items: [
  //       {
  //         title: "Introduction",
  //         url: "#",
  //       },
  //       {
  //         title: "Get Started",
  //         url: "#",
  //       },
  //       {
  //         title: "Tutorials",
  //         url: "#",
  //       },
  //       {
  //         title: "Changelog",
  //         url: "#",
  //       },
  //     ],
  //   },
  //   {
  //     title: "Settings",
  //     url: "#",
  //     icon: Settings2,
  //     items: [
  //       {
  //         title: "General",
  //         url: "#",
  //       },
  //       {
  //         title: "Team",
  //         url: "#",
  //       },
  //       {
  //         title: "Billing",
  //         url: "#",
  //       },
  //       {
  //         title: "Limits",
  //         url: "#",
  //       },
  //     ],
  //   },
  ],
}


type User = {
  id: string;
  name: string;
  email: string;
  avatar: string;
  about?: string;
}
 
type Travel = {
  id: string
  name: string
  icon: LucideIcon
}


export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const [user, setUser] = useState<User | null>(null)
  const [travels, setTravels] = useState<Travel[]>([])
  const [showForm, setShowForm] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem("token")
    const userId = localStorage.getItem("user_id")

    async function fetchUserAndTrips() {
      if (!token || !userId) {
        console.log("Brak tokena lub ID użytkownika, przerywam pobieranie danych.")
        return
      }

      try {
        const userRes = await fetch(`http://localhost:8000/users/${userId}`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        const userData = await userRes.json()
        const avatar = `https://api.dicebear.com/7.x/initials/svg?seed=${userData.name}`
        setUser({
          id: userId,
          name: userData.name,
          email: userData.email,
          avatar,
          about: userData.about,
        })

        const tripsRes = await fetch(`http://localhost:8000/trips/user/${userId}`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        const tripsData = await tripsRes.json()

        const mappedTravels = tripsData.map((trip: any) => ({
          id: trip._id,
          name: trip.name,
          icon: Flag,
        }))

        setTravels(mappedTravels)
      } catch (error) {
        console.error("Błąd podczas pobierania usera lub podróży:", error)
      }
    }

    if (token && userId) {
      fetchUserAndTrips()
    }
  }, [])

  const handleCancelForm = () => {
    setShowForm(false)
    document.activeElement instanceof HTMLElement && document.activeElement.blur()
  }

  const handleTripCreated = (newTrip: { _id: string; name: string }) => {
    setTravels((prev) => [
      ...prev,
      {
        id: newTrip._id,
        name: newTrip.name,
        icon: Flag,
      },
    ])
  }

  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
      <Link href="/" passHref>
    <LogoButton />
      </Link> 
      </SidebarHeader>

      <SidebarContent>
        <NavMain items={data.navMain} />

        <SidebarGroup>
          <SidebarMenu className="mb-2">
            <SidebarMenuItem>
              <SidebarMenuButton
                onClick={() => setShowForm(!showForm)}
                tooltip="Create Trip"
                className="gap-2 justify-start group-data-[collapsible=icon]:justify-center"
              >
                <Plus className="w-4 h-4" />
                <span className="group-data-[collapsible=icon]:hidden">Create Trip</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>

          {showForm && (
            <div className="px-4 mt-2 group-data-[collapsible=icon]:hidden">
              <TripCreateForm
                onCancel={handleCancelForm}
                onTripCreated={handleTripCreated}
              />
            </div>
          )}
        </SidebarGroup>

        <NavTravels travels={travels} setTravels={setTravels} />
      </SidebarContent>

      <SidebarFooter>{user && <NavUser user={user} />}</SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}