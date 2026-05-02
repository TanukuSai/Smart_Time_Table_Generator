import axios from 'axios'

// In production, VITE_API_URL points to the Koyeb backend (e.g. https://sttg-api-<your-org>.koyeb.app/api)
// In dev, the Vite proxy handles /api → localhost:8000
const baseURL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({ baseURL })

api.interceptors.request.use(cfg => {
  const stored = localStorage.getItem('sttg_user')
  if (stored) {
    cfg.headers.Authorization = `Bearer ${JSON.parse(stored).token}`
  }
  return cfg
})

export default api
