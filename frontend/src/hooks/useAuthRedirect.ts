// hooks/useAuthRedirect.ts
import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

export function useAuthRedirect() {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const publicPaths = ["/login", "/register"];

    // Sprawdzamy, czy bieżąca ścieżka jest publiczna
    const isPublicPath = publicPaths.includes(pathname);

    const token = localStorage.getItem("token");

    if (!token && !isPublicPath) {
      router.push("/login");
    }
  }, [pathname, router]);
}