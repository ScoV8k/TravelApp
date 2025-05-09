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
  BookOpen,
  Bot,
  Command,
  Flag,
  GalleryVerticalEnd,
  Map,
  PieChart,
  Settings2,
  SquareTerminal,
  Plus,
} from "lucide-react"

import { type LucideIcon } from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavTravels } from "@/components/nav-travels"
import { NavUser } from "@/components/nav-user"
import { useRouter } from "next/navigation"
import { TeamSwitcher } from "@/components/team-switcher"
import { useState, useEffect } from "react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"
import { LogoButton } from "./logo-button"
import { Button } from "./ui/button"
import { TripCreateForm } from "@/components/trip-create-form"

// This is sample data.
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
      title: "Playground",
      url: "#",
      icon: SquareTerminal,
      isActive: true,
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
    {
      title: "Models",
      url: "#",
      icon: Bot,
      items: [
        {
          title: "Genesis",
          url: "#",
        },
        {
          title: "Explorer",
          url: "#",
        },
        {
          title: "Quantum",
          url: "#",
        },
      ],
    },
    {
      title: "Documentation",
      url: "#",
      icon: BookOpen,
      items: [
        {
          title: "Introduction",
          url: "#",
        },
        {
          title: "Get Started",
          url: "#",
        },
        {
          title: "Tutorials",
          url: "#",
        },
        {
          title: "Changelog",
          url: "#",
        },
      ],
    },
    {
      title: "Settings",
      url: "#",
      icon: Settings2,
      items: [
        {
          title: "General",
          url: "#",
        },
        {
          title: "Team",
          url: "#",
        },
        {
          title: "Billing",
          url: "#",
        },
        {
          title: "Limits",
          url: "#",
        },
      ],
    },
  ],
}


type User = {
  name: string
  email: string
  avatar: string
}
 
type Travel = {
  id: string
  name: string
  icon: LucideIcon
}


// export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
//   const [user, setUser] = useState<User | null>(null)
//   const [travels, setTravels] = useState<Travel[]>([])

//   useEffect(() => {
//     const token = localStorage.getItem("token")
//     const userId = localStorage.getItem("user_id")

//     async function fetchUserAndTrips() {
//       try {
//         // 1. Pobierz dane użytkownika
//         const userRes = await fetch(`http://localhost:8000/users/${userId}`, {
//           headers: {
//             Authorization: `Bearer ${token}`,
//           },
//         })
//         const userData = await userRes.json()

//         const avatar = `https://api.dicebear.com/7.x/initials/svg?seed=${userData.name}`
//         setUser({
//           name: userData.name,
//           email: userData.email,
//           avatar,
//         })

//         // 2. Pobierz listę podróży użytkownika
//         const tripsRes = await fetch(`http://localhost:8000/trips/user/${userId}`, {
//           headers: {
//             Authorization: `Bearer ${token}`,
//           },
//         })
//         const tripsData = await tripsRes.json()

//         // 3. Zmapuj podróże do formatu dla NavTravels
//         // const mappedTravels = tripsData.map((trip: any) => ({
//         //   name: trip.name,
//         //   url: `/trip/${trip._id}`, // możesz potem przekierowywać do konkretnego czatu lub podsumowania
//         //   icon: Flag,
//         // }))
//         const mappedTravels = tripsData.map((trip: any) => ({
//           id: trip._id,
//           name: trip.name,
//           icon: Flag,
//         }))
        
//         setTravels(mappedTravels)

//       } catch (error) {
//         console.error("Błąd podczas pobierania usera lub podróży:", error)
//       }
//     }

//     if (token && userId) {
//       fetchUserAndTrips()
//     }
//   }, [])

//   return (
//     <Sidebar collapsible="icon" {...props}>
//       <SidebarHeader>
//         {/* <TeamSwitcher teams={data.teams} /> */}
//         <LogoButton></LogoButton>
//       </SidebarHeader>
//       <SidebarContent>
//         <NavMain items={data.navMain} />
//         <Button></Button>
//         <NavTravels travels={travels} />
//       </SidebarContent>
//       <SidebarFooter>
//       {user && <NavUser user={user} />}
//       </SidebarFooter>
//       <SidebarRail />
//     </Sidebar>
//   )
// }


export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const [user, setUser] = useState<User | null>(null)
  const [travels, setTravels] = useState<Travel[]>([])
  const [showForm, setShowForm] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const token = localStorage.getItem("token")
    const userId = localStorage.getItem("user_id")

    async function fetchUserAndTrips() {
      try {
        const userRes = await fetch(`http://localhost:8000/users/${userId}`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        const userData = await userRes.json()
        const avatar = `https://api.dicebear.com/7.x/initials/svg?seed=${userData.name}`
        setUser({
          name: userData.name,
          email: userData.email,
          avatar,
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
    // reset focus, usuń "outline" z buttona jeśli został kliknięty
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

        {/* GRUPA: Create Trip */}
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

          {/* FORM widoczny tylko przy rozwiniętym sidebarze */}
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