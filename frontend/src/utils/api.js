import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(cfg => {
  const stored = localStorage.getItem('sttg_user')
  if (stored) {
    cfg.headers.Authorization = `Bearer ${JSON.parse(stored).token}`
  }
  return cfg
})

export default api
