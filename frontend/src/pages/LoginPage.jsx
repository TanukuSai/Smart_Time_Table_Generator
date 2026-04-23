import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../utils/api'
import toast from 'react-hot-toast'
import { UserPlus, LogIn, ArrowLeft } from 'lucide-react'

const DEMO_ACCOUNTS = [
  { label: 'Admin', email: 'admin@tkrec.edu', password: 'admin123', role: 'admin' },
  { label: 'Faculty', email: 'sharma@tkrec.edu', password: 'faculty123', role: 'faculty' },
  { label: 'Student (CSE-A)', email: 'btech-cse-a@tkrec.edu', password: 'student123', role: 'student' },
]

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [mode, setMode] = useState('login') // 'login' | 'register'
  const [regName, setRegName] = useState('')
  const [regEmail, setRegEmail] = useState('')
  const [regPassword, setRegPassword] = useState('')
  const [regInstitution, setRegInstitution] = useState('')
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const { data } = await api.post('/auth/login', { email, password })
      login(data)
      toast.success(`Welcome, ${data.name}`)
      if (data.role === 'admin') navigate('/admin/dashboard')
      else if (data.role === 'faculty') navigate('/faculty/dashboard')
      else navigate('/student/timetable')
    } catch {
      toast.error('Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    if (!regName || !regEmail || !regPassword) {
      toast.error('Please fill all fields')
      return
    }
    setLoading(true)
    try {
      const { data } = await api.post('/auth/register', {
        name: regName,
        email: regEmail,
        password: regPassword,
        institution: regInstitution,
      })
      login(data)
      toast.success(`Welcome, ${data.name}! Your admin account is ready.`)
      navigate('/admin/dashboard')
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  const quickLogin = (acc) => {
    setEmail(acc.email)
    setPassword(acc.password)
  }

  return (
    <div style={{
      minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'var(--navy)', padding: '20px',
      backgroundImage: 'radial-gradient(ellipse 80% 50% at 50% -20%, rgba(245,158,11,0.08), transparent)'
    }}>
      <div style={{ width: '100%', maxWidth: '420px' }}>
        {/* Logo */}
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            width: 56, height: 56, borderRadius: 16,
            background: 'linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.05))',
            border: '1px solid rgba(245,158,11,0.3)',
            marginBottom: 16, fontSize: 24
          }}>📅</div>
          <h1 style={{ fontSize: 26, fontFamily: 'var(--font-display)', letterSpacing: '-0.02em' }}>
            STTG
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: 13, marginTop: 6 }}>
            Smart Time Table Generator
          </p>
        </div>

        {mode === 'login' ? (
          <>
            {/* Login Card */}
            <div className="card" style={{ padding: '28px 32px' }}>
              <h2 style={{ fontSize: 18, marginBottom: 24, display: 'flex', alignItems: 'center', gap: 8 }}>
                <LogIn size={18} /> Sign in to your account
              </h2>
              <form onSubmit={handleLogin}>
                <label>Email address</label>
                <input type="email" placeholder="you@university.edu" value={email} onChange={e => setEmail(e.target.value)} required />
                <label>Password</label>
                <input type="password" placeholder="••••••••" value={password} onChange={e => setPassword(e.target.value)} required />
                <button className="btn btn-primary" type="submit" disabled={loading}
                  style={{ width: '100%', justifyContent: 'center', marginTop: 20, padding: '11px' }}>
                  {loading ? <><span className="spinner" style={{ width: 15, height: 15 }} /> Signing in...</> : 'Sign in'}
                </button>
              </form>
              <div style={{ textAlign: 'center', marginTop: 16 }}>
                <button className="btn btn-ghost btn-sm" onClick={() => setMode('register')}
                  style={{ fontSize: 13, gap: 6 }}>
                  <UserPlus size={14} /> Create Admin Account
                </button>
              </div>
            </div>

            {/* Demo accounts */}
            <div style={{ marginTop: 20 }}>
              <p style={{ color: 'var(--text-muted)', fontSize: 12, textAlign: 'center', marginBottom: 10, textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                Demo accounts
              </p>
              <div style={{ display: 'flex', gap: 8 }}>
                {DEMO_ACCOUNTS.map(acc => (
                  <button key={acc.role + acc.email} onClick={() => quickLogin(acc)}
                    className="btn btn-ghost btn-sm"
                    style={{ flex: 1, justifyContent: 'center', fontSize: 12 }}>
                    {acc.label}
                  </button>
                ))}
              </div>
            </div>
          </>
        ) : (
          /* Register Card */
          <div className="card" style={{ padding: '28px 32px' }}>
            <h2 style={{ fontSize: 18, marginBottom: 24, display: 'flex', alignItems: 'center', gap: 8 }}>
              <UserPlus size={18} /> Create Admin Account
            </h2>
            <form onSubmit={handleRegister}>
              <label>Full Name</label>
              <input type="text" placeholder="Dr. John Smith" value={regName} onChange={e => setRegName(e.target.value)} required />
              <label>Email Address</label>
              <input type="email" placeholder="admin@university.edu" value={regEmail} onChange={e => setRegEmail(e.target.value)} required />
              <label>Password</label>
              <input type="password" placeholder="Minimum 6 characters" value={regPassword} onChange={e => setRegPassword(e.target.value)} required />
              <label>Institution Name <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>(optional)</span></label>
              <input type="text" placeholder="e.g. TKREC" value={regInstitution} onChange={e => setRegInstitution(e.target.value)} />
              <button className="btn btn-primary" type="submit" disabled={loading}
                style={{ width: '100%', justifyContent: 'center', marginTop: 20, padding: '11px' }}>
                {loading ? <><span className="spinner" style={{ width: 15, height: 15 }} /> Creating...</> : 'Create Account & Sign In'}
              </button>
            </form>
            <div style={{ textAlign: 'center', marginTop: 16 }}>
              <button className="btn btn-ghost btn-sm" onClick={() => setMode('login')}
                style={{ fontSize: 13, gap: 6 }}>
                <ArrowLeft size={14} /> Back to Sign In
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
