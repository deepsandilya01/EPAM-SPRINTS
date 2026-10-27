import axios from 'axios'

export const DATA_MODE = (import.meta.env.VITE_DATA_MODE as 'mock' | 'live') || 'mock'
export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
})

// Add response interceptor for unified error formatting
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'API request failed'
    console.error(`[API Error ${error.config?.url}]:`, message)
    return Promise.reject(new Error(message))
  }
)
