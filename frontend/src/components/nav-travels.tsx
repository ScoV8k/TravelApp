
import {
  Folder,
  Forward,
  MoreHorizontal,
  Trash2,
  type LucideIcon,
} from "lucide-react"

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  useSidebar,
} from "@/components/ui/sidebar"

import { useState } from "react"

export function NavTravels({
  travels,
}: {
  travels: {
    id: string
    name: string
    icon: LucideIcon
  }[]
}) {
  const { isMobile } = useSidebar()
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editingValue, setEditingValue] = useState("")

  const handleDelete = async (id: string) => {
    const confirmed = confirm("Czy na pewno chcesz usunąć tę podróż?")
    if (!confirmed) return

    try {
      const token = localStorage.getItem("token")
      const res = await fetch(`http://localhost:8000/trips/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (!res.ok) throw new Error("Usuwanie nie powiodło się")

      window.location.reload()
    } catch (error) {
      console.error("Błąd podczas usuwania:", error)
    }
  }

  const handleRename = (id: string, currentName: string) => {
    setEditingId(id)
    setEditingValue(currentName)
  }

  const handleRenameSubmit = async (id: string) => {
    try {
      const token = localStorage.getItem("token")
      const res = await fetch(`http://localhost:8000/trips/${id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ name: editingValue }),
      })

      if (!res.ok) throw new Error("Zmiana nazwy nie powiodła się")
      window.location.reload()
    } catch (error) {
      console.error("Błąd podczas zmiany nazwy:", error)
    } finally {
      setEditingId(null)
    }
  }


  return (
    <SidebarGroup className="group-data-[collapsible=icon]:hidden">
      <SidebarGroupLabel>Trips</SidebarGroupLabel>
      <SidebarMenu>
        {travels.map((item) => (
          <SidebarMenuItem key={item.id}>
            <SidebarMenuButton asChild>
              {editingId === item.id ? (
                <div className="flex items-center gap-2 w-full">
                  <item.icon className="shrink-0" />
                  <input
                    autoFocus
                    className="text-sm bg-transparent border-b border-gray-300 outline-none w-full"
                    value={editingValue}
                    onChange={(e) => setEditingValue(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") {
                        handleRenameSubmit(item.id)
                      } else if (e.key === "Escape") {
                        setEditingId(null)
                      }
                    }}
                    onBlur={() => handleRenameSubmit(item.id)}
                  />
                </div>
              ) : (
                <a href={`/trip/${item.id}`}>
                  <item.icon />
                  <span>{item.name}</span>
                </a>
              )}
            </SidebarMenuButton>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuAction showOnHover>
                  <MoreHorizontal />
                  <span className="sr-only">More</span>
                </SidebarMenuAction>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className="w-48 rounded-lg"
                side={isMobile ? "bottom" : "right"}
                align={isMobile ? "end" : "start"}
              >
                <DropdownMenuItem onClick={() => handleRename(item.id, item.name)}>
                  <Forward className="text-muted-foreground" />
                  <span>Rename Travel</span>
                </DropdownMenuItem>

                <DropdownMenuItem asChild>
                  <a href={`/trip/${item.id}`} className="flex items-center gap-2">
                    <Folder className="text-muted-foreground" />
                    <span>View Travel</span>
                  </a>
                </DropdownMenuItem>

                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => handleDelete(item.id)}>
                  <Trash2 className="text-muted-foreground mr-2" />
                  <span>Delete Travel</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </SidebarGroup>
  )
}


// import {
//   Folder,
//   MoreHorizontal,
//   Trash2,
//   type LucideIcon,
// } from "lucide-react";

// import {
//   DropdownMenu,
//   DropdownMenuContent,
//   DropdownMenuItem,
//   DropdownMenuSeparator,
//   DropdownMenuTrigger,
// } from "@/components/ui/dropdown-menu";
// import {
//   SidebarGroup,
//   SidebarGroupLabel,
//   SidebarMenu,
//   SidebarMenuAction,
//   SidebarMenuButton,
//   SidebarMenuItem,
//   useSidebar,
// } from "@/components/ui/sidebar";

// export function NavTravels({
//   travels,
// }: {
//   travels: {
//     name: string;
//     url: string;
//     icon: LucideIcon;
//     flag?: string; // Dodajemy flagę!
//   }[];
// }) {
//   const { isMobile } = useSidebar();

//   return (
//     <SidebarGroup className="group-data-[collapsible=icon]:hidden">
//       <SidebarGroupLabel>Trips</SidebarGroupLabel>
//       <SidebarMenu>
//         {travels.map((item) => (
//           <SidebarMenuItem key={item.name} className="h-16">
//             <div className="flex items-center justify-between w-full h-full px-3 py-2">
//               <a href={item.url} className="flex items-center gap-3">
//                 {/* Logo flagi */}
//                 <div className="size-10 rounded-md overflow-hidden bg-muted flex items-center justify-center">
//                   {item.flag ? (
//                     <img
//                       src={item.flag}
//                       alt={`${item.name} flag`}
//                       className="object-cover w-full h-full"
//                     />
//                   ) : (
//                     <item.icon className="w-6 h-6 text-muted-foreground" />
//                   )}
//                 </div>

//                 {/* Nazwa tripa */}
//                 <span className="text-sm truncate">{item.name}</span>
//               </a>

//               <DropdownMenu>
//                 <DropdownMenuTrigger asChild>
//                   <SidebarMenuAction
//                     showOnHover
//                     className="flex items-center justify-center focus:outline-none focus-visible:ring-0 focus-visible:ring-offset-0"
//                   >
//                     <MoreHorizontal className="w-7 h-7" />
//                     <span className="sr-only">More</span>
//                   </SidebarMenuAction>
//                 </DropdownMenuTrigger>

//                 <DropdownMenuContent
//                   className="w-48 rounded-lg"
//                   side={isMobile ? "bottom" : "right"}
//                   align={isMobile ? "end" : "start"}
//                 >
//                   <DropdownMenuItem asChild>
//                     <a href={item.url} className="flex items-center gap-2">
//                       <Folder className="text-muted-foreground" />
//                       <span>View Travel</span>
//                     </a>
//                   </DropdownMenuItem>
//                   <DropdownMenuSeparator />
//                   <DropdownMenuItem>
//                     <Trash2 className="text-muted-foreground" />
//                     <span>Delete Travel</span>
//                   </DropdownMenuItem>
//                 </DropdownMenuContent>
//               </DropdownMenu>
//             </div>
//           </SidebarMenuItem>
//         ))}
//       </SidebarMenu>
//     </SidebarGroup>
//   );
// }
