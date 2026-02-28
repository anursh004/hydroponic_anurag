"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { useFarmStore } from "@/stores/farm-store";
import { farmApi } from "@/lib/api";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { PageLoader } from "@/components/ui/loading";

export default function AuthenticatedLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, fetchUser, user } = useAuthStore();
  const { setFarms, setCurrentFarm, currentFarm } = useFarmStore();

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      router.replace("/login");
      return;
    }
    if (!user) {
      fetchUser();
    }
  }, [router, fetchUser, user]);

  useEffect(() => {
    if (user && !currentFarm) {
      farmApi.list().then(({ data }) => {
        const farms = data.items || [];
        setFarms(farms);
        if (farms.length > 0) {
          const savedId = localStorage.getItem("current_farm_id");
          const farm = farms.find((f: any) => f.id === savedId) || farms[0];
          setCurrentFarm(farm);
        }
      }).catch(() => {});
    }
  }, [user, currentFarm, setFarms, setCurrentFarm]);

  if (!user) return <PageLoader />;

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 bg-gray-50">
          {children}
        </main>
      </div>
    </div>
  );
}
