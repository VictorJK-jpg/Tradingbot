import { create } from "zustand";
import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "auth_tokens";

const useAuthStore = create((set, get) => ({
  // State
  user: null,
  tokens: null,
  isLoading: true,

  // Actions
  setTokens: async (tokens) => {
    await SecureStore.setItemAsync(TOKEN_KEY, JSON.stringify(tokens));
    set({ tokens, isLoading: false });
  },

  loadTokens: async () => {
    try {
      const raw = await SecureStore.getItemAsync(TOKEN_KEY);
      if (raw) {
        set({ tokens: JSON.parse(raw), isLoading: false });
      } else {
        set({ isLoading: false });
      }
    } catch {
      set({ isLoading: false });
    }
  },

  clearTokens: async () => {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    set({ tokens: null, user: null });
  },

  setUser: (user) => set({ user }),

  getAccessToken: () => get().tokens?.access_token,
}));

export default useAuthStore;
