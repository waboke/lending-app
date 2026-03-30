import axios from 'axios'

const token = localStorage.getItem('access_token')

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  headers: token ? { Authorization: `Bearer ${token}` } : {},
})

export const setAuthToken = (accessToken) => {
  if (accessToken) {
    localStorage.setItem('access_token', accessToken)
    api.defaults.headers.Authorization = `Bearer ${accessToken}`
  } else {
    localStorage.removeItem('access_token')
    delete api.defaults.headers.Authorization
  }
}
