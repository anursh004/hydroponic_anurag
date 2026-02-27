import { create } from "zustand";
import type { Farm } from "@/types";

interface FarmState {
  currentFarm: Farm | null;
  farms: Farm[];
  setCurrentFarm: (farm: Farm) => void;
  setFarms: (farms: Farm[]) => void;
}

export const useFarmStore = create<FarmState>((set) => ({
  currentFarm: null,
  farms: [],

  setCurrentFarm: (farm) => {
    if (typeof window !== "undefined") {
      localStorage.setItem("current_farm_id", farm.id);
    }
    set({ currentFarm: farm });
  },

  setFarms: (farms) => set({ farms }),
}));
