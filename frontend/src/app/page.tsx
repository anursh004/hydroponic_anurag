"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    router.replace(token ? "/dashboard" : "/login");
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-300 border-t-primary-600" />
    </div>
  );
}
