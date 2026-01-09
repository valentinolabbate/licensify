import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { authApi } from '../services/api'

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: true,
      
      setToken: (token) => {
        set({ token })
      },
      
      login: async (email, password) => {
        const response = await authApi.login({ email, password })
        const { access_token, refresh_token } = response.data
        
        set({
          token: access_token,
          refreshToken: refresh_token,
          isAuthenticated: true,
        })
        
        // Fetch user info
        const userResponse = await authApi.getMe()
        set({ user: userResponse.data })
        
        return response.data
      },
      
      register: async (email, password, fullName) => {
        const response = await authApi.register({
          email,
          password,
          full_name: fullName,
        })
        return response.data
      },
      
      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
        })
      },
      
      checkAuth: async () => {
        const token = get().token
        if (!token) {
          set({ isLoading: false })
          return false
        }
        
        try {
          const response = await authApi.getMe()
          set({
            user: response.data,
            isAuthenticated: true,
            isLoading: false,
          })
          return true
        } catch (error) {
          set({
            user: null,
            token: null,
            refreshToken: null,
            isAuthenticated: false,
            isLoading: false,
          })
          return false
        }
      },
      
      updateUser: (userData) => {
        set({ user: { ...get().user, ...userData } })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.checkAuth()
        }
      },
    }
  )
)
