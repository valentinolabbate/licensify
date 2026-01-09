import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
api.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor - handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    
    // If 401 and not a refresh attempt, try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const refreshToken = useAuthStore.getState().refreshToken
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken,
          })
          
          const { access_token } = response.data
          useAuthStore.getState().setToken(access_token)
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh failed - logout
          useAuthStore.getState().logout()
        }
      } else {
        useAuthStore.getState().logout()
      }
    }
    
    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  verifyEmail: (token) => api.post('/auth/verify-email', { token }),
  refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
  getMe: () => api.get('/auth/me'),
  changePassword: (data) => api.post('/auth/change-password', data),
}

// License API
export const licenseApi = {
  list: () => api.get('/licenses'),
  get: (id) => api.get(`/licenses/${id}`),
  create: (data) => api.post('/licenses', data),
  update: (id, data) => api.put(`/licenses/${id}`, data),
  delete: (id) => api.delete(`/licenses/${id}`),
  revoke: (id) => api.post(`/licenses/${id}/revoke`),
}

// Device API
export const deviceApi = {
  listByLicense: (licenseId) => api.get(`/devices/license/${licenseId}`),
  update: (id, data) => api.put(`/devices/${id}`, data),
  block: (id) => api.post(`/devices/${id}/block`),
  unblock: (id) => api.post(`/devices/${id}/unblock`),
  delete: (id) => api.delete(`/devices/${id}`),
}

// Admin API
export const adminApi = {
  getStats: () => api.get('/admin/stats'),
  listUsers: (params) => api.get('/admin/users', { params }),
  toggleAdmin: (userId) => api.put(`/admin/users/${userId}/toggle-admin`),
  toggleActive: (userId) => api.put(`/admin/users/${userId}/toggle-active`),
  approveUser: (userId) => api.put(`/admin/users/${userId}/approve`),
  rejectUser: (userId) => api.put(`/admin/users/${userId}/reject`),
}

// Revenue API (Admin)
export const revenueApi = {
  list: (params) => api.get('/admin/revenue', { params }),
  getSummary: () => api.get('/admin/revenue/summary'),
  create: (data) => api.post('/admin/revenue', data),
  getForLicense: (licenseId) => api.get(`/admin/revenue/license/${licenseId}`),
  delete: (id) => api.delete(`/admin/revenue/${id}`),
  extendLicense: (licenseId, data) => api.post(`/admin/revenue/license/${licenseId}/extend`, data),
}

export default api
