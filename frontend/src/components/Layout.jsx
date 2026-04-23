import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import {
  LayoutDashboard, CalendarDays, Users, DoorOpen,
  ClipboardList, Wand2, Calendar, LogOut, FileText, Eye,
  BookOpen, GraduationCap, Shield, History
} from 'lucide-react'

const NAV = {
  admin: [
    { icon: LayoutDashboard, label: 'Dashboard', to: '/admin/dashboard' },
    { icon: CalendarDays, label: 'Timetable', to: '/admin/timetable' },
    { icon: BookOpen, label: 'Subjects', to: '/admin/subjects' },
    { icon: Users, label: 'Faculty', to: '/admin/faculty' },
    { icon: GraduationCap, label: 'Departments', to: '/admin/departments' },
    { icon: DoorOpen, label: 'Rooms', to: '/admin/rooms' },
    { icon: Shield, label: 'Constraints', to: '/admin/constraints' },
    { icon: ClipboardList, label: 'Leaves', to: '/admin/leaves' },
    { icon: Wand2, label: 'Generate', to: '/admin/generate' },
    { icon: History, label: 'History', to: '/admin/history' },
  ],
  faculty: [
    { icon: LayoutDashboard, label: 'Dashboard', to: '/faculty/dashboard' },
    { icon: Calendar, label: 'My Schedule', to: '/faculty/schedule' },
    { icon: FileText, label: 'Leave Request', to: '/faculty/leave' },
  ],
  student: [
    { icon: CalendarDays, label: 'My Timetable', to: '/student/timetable' },
    { icon: Eye, label: 'Faculty Today', to: '/student/faculty-today' },
  ],
}

const ROLE_BADGE = {
  admin: { label: 'Admin', cls: 'badge-amber' },
  faculty: { label: 'Faculty', cls: 'badge-teal' },
  student: { label: 'Student', cls: 'badge-blue' },
}

function initials(name = '') {
  return name.split(' ').map(n => n[0]).filter(Boolean).slice(0, 2).join('').toUpperCase()
}

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const navItems = NAV[user?.role] || []
  const badge = ROLE_BADGE[user?.role] || {}

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* Sidebar */}
      <aside style={{
        width: 220, flexShrink: 0,
        background: 'var(--navy-mid)',
        borderRight: '1px solid var(--navy-border)',
        display: 'flex', flexDirection: 'column',
        overflow: 'hidden'
      }}>
        {/* Brand */}
        <div style={{ padding: '20px 18px 16px', borderBottom: '1px solid var(--navy-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 34, height: 34, borderRadius: 9,
              background: 'rgba(245,158,11,0.15)',
              border: '1px solid rgba(245,158,11,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 16, flexShrink: 0
            }}>📅</div>
            <div>
              <div style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 15, lineHeight: 1.1 }}>STTG</div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
                {user?.institution || 'Smart Timetable'}
              </div>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: '12px 10px', overflowY: 'auto' }}>
          {navItems.map(({ icon: Icon, label, to }) => (
            <NavLink key={to} to={to} style={{ display: 'block', textDecoration: 'none' }}>
              {({ isActive }) => (
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 10,
                  padding: '9px 12px', borderRadius: 'var(--radius-md)',
                  marginBottom: 2,
                  background: isActive ? 'rgba(245,158,11,0.1)' : 'transparent',
                  color: isActive ? 'var(--amber)' : 'var(--text-secondary)',
                  fontWeight: isActive ? 600 : 400,
                  fontSize: 13.5,
                  transition: 'all 150ms',
                  borderLeft: isActive ? '2px solid var(--amber)' : '2px solid transparent',
                }}>
                  <Icon size={15} />
                  {label}
                </div>
              )}
            </NavLink>
          ))}
        </nav>

        {/* User info */}
        <div style={{ padding: '14px 16px', borderTop: '1px solid var(--navy-border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
            <div className="avatar" style={{ width: 32, height: 32, fontSize: 11 }}>{initials(user?.name)}</div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontSize: 13, fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user?.name}</div>
              <span className={`badge ${badge.cls}`} style={{ fontSize: 10, padding: '1px 7px' }}>{badge.label}</span>
            </div>
          </div>
          <button className="btn btn-ghost btn-sm" style={{ width: '100%', justifyContent: 'center', fontSize: 12 }} onClick={handleLogout}>
            <LogOut size={13} /> Sign out
          </button>
        </div>
      </aside>

      {/* Main */}
      <main style={{ flex: 1, overflow: 'auto', padding: '28px 32px', background: 'var(--navy)' }}>
        <Outlet />
      </main>
    </div>
  )
}
