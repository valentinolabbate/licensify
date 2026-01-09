import { create } from 'zustand'
import { licenseApi, deviceApi } from '../services/api'

export const useLicenseStore = create((set, get) => ({
  licenses: [],
  selectedLicense: null,
  devices: [],
  isLoading: false,
  error: null,
  
  fetchLicenses: async () => {
    set({ isLoading: true, error: null })
    try {
      const response = await licenseApi.list()
      set({ licenses: response.data.licenses, isLoading: false })
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Failed to fetch licenses', isLoading: false })
    }
  },
  
  fetchLicense: async (id) => {
    set({ isLoading: true, error: null })
    try {
      const response = await licenseApi.get(id)
      set({ selectedLicense: response.data, isLoading: false })
      return response.data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Failed to fetch license', isLoading: false })
      throw error
    }
  },
  
  createLicense: async (data) => {
    set({ isLoading: true, error: null })
    try {
      const response = await licenseApi.create(data)
      set(state => ({
        licenses: [response.data, ...state.licenses],
        isLoading: false,
      }))
      return response.data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Failed to create license', isLoading: false })
      throw error
    }
  },
  
  updateLicense: async (id, data) => {
    set({ isLoading: true, error: null })
    try {
      const response = await licenseApi.update(id, data)
      set(state => ({
        licenses: state.licenses.map(l => l.id === id ? response.data : l),
        selectedLicense: state.selectedLicense?.id === id ? response.data : state.selectedLicense,
        isLoading: false,
      }))
      return response.data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Failed to update license', isLoading: false })
      throw error
    }
  },
  
  deleteLicense: async (id) => {
    set({ isLoading: true, error: null })
    try {
      await licenseApi.delete(id)
      set(state => ({
        licenses: state.licenses.filter(l => l.id !== id),
        selectedLicense: state.selectedLicense?.id === id ? null : state.selectedLicense,
        isLoading: false,
      }))
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Failed to delete license', isLoading: false })
      throw error
    }
  },
  
  revokeLicense: async (id) => {
    set({ isLoading: true, error: null })
    try {
      const response = await licenseApi.revoke(id)
      set(state => ({
        licenses: state.licenses.map(l => l.id === id ? response.data : l),
        selectedLicense: state.selectedLicense?.id === id ? response.data : state.selectedLicense,
        isLoading: false,
      }))
      return response.data
    } catch (error) {
      set({ error: error.response?.data?.detail || 'Failed to revoke license', isLoading: false })
      throw error
    }
  },
  
  // Device actions
  blockDevice: async (deviceId) => {
    try {
      const response = await deviceApi.block(deviceId)
      // Update device in selectedLicense
      set(state => {
        if (!state.selectedLicense) return state
        return {
          selectedLicense: {
            ...state.selectedLicense,
            devices: state.selectedLicense.devices.map(d => 
              d.id === deviceId ? response.data : d
            ),
          },
        }
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  unblockDevice: async (deviceId) => {
    try {
      const response = await deviceApi.unblock(deviceId)
      set(state => {
        if (!state.selectedLicense) return state
        return {
          selectedLicense: {
            ...state.selectedLicense,
            devices: state.selectedLicense.devices.map(d => 
              d.id === deviceId ? response.data : d
            ),
          },
        }
      })
      return response.data
    } catch (error) {
      throw error
    }
  },
  
  deleteDevice: async (deviceId) => {
    try {
      await deviceApi.delete(deviceId)
      set(state => {
        if (!state.selectedLicense) return state
        return {
          selectedLicense: {
            ...state.selectedLicense,
            devices: state.selectedLicense.devices.filter(d => d.id !== deviceId),
            current_devices: state.selectedLicense.current_devices - 1,
          },
        }
      })
    } catch (error) {
      throw error
    }
  },
  
  clearError: () => set({ error: null }),
  clearSelected: () => set({ selectedLicense: null }),
}))
