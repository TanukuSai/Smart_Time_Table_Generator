import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { AlertTriangle, Clock, CheckCircle, Users, BookOpen, DoorOpen, CalendarDays, Shield, RefreshCw, UserCheck } from 'lucide-react'
import api from '../../utils/api'

export default function Dashboard() {
  const [faculty, setFaculty] = useState([])
  const [leaves, setLeaves] = useState([])
  const [subjects, setSubjects] = useState([])
  const [rooms, setRooms] = useState([])
  const [departments, setGrades] = useState([])
  const [substitutions, setSubstitutions] = useState([])
  const navigate = useNavigate()

  useEffect(() => {
    const todayStr = new Date().toLocaleDateString('en-CA')
    api.get(`/faculty?date=${todayStr}`).then(r => setFaculty(r.data)).catch(() => {})
    api.get('/leaves').then(r => setLeaves(r.data)).catch(() => {})
    api.get('/rooms').then(r => setRooms(r.data)).catch(() => {})
    api.get('/departments').then(r => setGrades(r.data)).catch(() => {})
    api.get('/subjects').then(r => setSubjects(r.data)).catch(() => {})
    api.get('/leaves/substitutions').then(r => setSubstitutions(r.data)).catch(() => {})
  }, [])

  const absent = faculty.filter(f => !f.is_present)
  const pending = leaves.filter(l => l.status === 'pending')
  const today = new Date().toLocaleDateString('en-CA')
  const todaySubs = substitutions.filter(s => s.leave_date === today)
  const filledToday = todaySubs.filter(s => s.substitute_faculty_name)
  const unfilledToday = todaySubs.filter(s => !s.substitute_faculty_name)

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Admin Dashboard</h2>
        <p>Teegala Krishna Reddy Engineering College — Overview</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 12, marginBottom: 20 }}>
        <div className="metric-card">
          <div className="flex gap-2" style={{ marginBottom: 10 }}><Users size={16} color="var(--amber)" /><span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Faculty</span></div>
          <div className="metric-val">{faculty.length}</div>
          <div className="metric-lbl">{absent.length} absent today</div>
        </div>
        <div className="metric-card">
          <div className="flex gap-2" style={{ marginBottom: 10 }}><CalendarDays size={16} color="var(--teal)" /><span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Classes</span></div>
          <div className="metric-val" style={{ color: 'var(--teal)' }}>{departments.length}</div>
          <div className="metric-lbl">Active departments</div>
        </div>
        <div className="metric-card">
          <div className="flex gap-2" style={{ marginBottom: 10 }}><DoorOpen size={16} color="#93c5fd" /><span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Rooms</span></div>
          <div className="metric-val" style={{ color: '#93c5fd' }}>{rooms.length}</div>
          <div className="metric-lbl">{rooms.filter(r => r.is_available).length} available</div>
        </div>
        <div className="metric-card">
          <div className="flex gap-2" style={{ marginBottom: 10 }}><Clock size={16} color="var(--rose)" /><span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Leaves</span></div>
          <div className="metric-val" style={{ color: 'var(--rose)' }}>{pending.length}</div>
          <div className="metric-lbl">Pending approval</div>
        </div>
        <div className="metric-card">
          <div className="flex gap-2" style={{ marginBottom: 10 }}><RefreshCw size={16} color="var(--amber)" /><span style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Subs</span></div>
          <div className="metric-val" style={{ color: 'var(--amber)' }}>{todaySubs.length}</div>
          <div className="metric-lbl">{filledToday.length} filled, {unfilledToday.length} unfilled</div>
        </div>
      </div>

      <div className="grid2">
        <div>
          <div className="card">
            <div className="flex-between mb-4" style={{ marginBottom: 14 }}><h3 style={{ fontSize: 15 }}>Today's Alerts</h3></div>
            {absent.length > 0 && absent.map(f => (
              <div key={f.id} className="alert alert-danger">
                <AlertTriangle size={15} style={{ flexShrink: 0, marginTop: 1 }} />
                <span><strong>{f.name}</strong> is absent. Departments: {f.grade_subjects?.map(g => g.grade_name).filter((v,i,a)=>a.indexOf(v)===i).join(', ') || '—'}</span>
              </div>
            ))}
            {pending.length > 0 && (
              <div className="alert alert-warn"><Clock size={15} style={{ flexShrink: 0, marginTop: 1 }} /><span>{pending.length} leave request{pending.length > 1 ? 's' : ''} awaiting approval.</span></div>
            )}
            {unfilledToday.length > 0 && (
              <div className="alert alert-warn"><AlertTriangle size={15} style={{ flexShrink: 0, marginTop: 1 }} /><span>{unfilledToday.length} substitution slot{unfilledToday.length > 1 ? 's' : ''} unfilled today!</span></div>
            )}
            {absent.length === 0 && pending.length === 0 && unfilledToday.length === 0 && (
              <div className="alert alert-success"><CheckCircle size={15} /><span>All faculty present. No pending requests.</span></div>
            )}
          </div>

          {todaySubs.length > 0 && (
            <div className="card">
              <div className="flex-between" style={{ marginBottom: 14 }}>
                <h3 style={{ fontSize: 15, display: 'flex', alignItems: 'center', gap: 6 }}><RefreshCw size={14} color="var(--amber)" /> Today's Substitutions</h3>
                <button className="btn btn-ghost btn-sm" onClick={() => navigate('/admin/leaves')}>View all</button>
              </div>
              {todaySubs.slice(0, 5).map((s, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '8px 0', borderBottom: '1px solid var(--navy-border)' }}>
                  <div style={{ width: 3, height: 28, borderRadius: 2, background: s.substitute_faculty_name ? 'var(--green)' : 'var(--rose)', flexShrink: 0 }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13 }}><strong>{s.subject_name}</strong> · {s.department_name}</div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                      {s.day} {s.slot_time} · {s.original_faculty_name} →{' '}
                      {s.substitute_faculty_name ? <span style={{ color: 'var(--green)', fontWeight: 600 }}>{s.substitute_faculty_name}</span> : <span style={{ color: 'var(--rose)' }}>Unfilled</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {pending.length > 0 && (
            <div className="card">
              <div className="flex-between" style={{ marginBottom: 14 }}>
                <h3 style={{ fontSize: 15 }}>Pending Leaves</h3>
                <button className="btn btn-ghost btn-sm" onClick={() => navigate('/admin/leaves')}>View all</button>
              </div>
              {pending.slice(0, 3).map(l => (
                <div key={l.id} className="leave-card" style={{ marginBottom: 8 }}>
                  <div className="avatar avatar-teal" style={{ fontSize: 11 }}>{(l.faculty_name || 'U').split(' ').map(n => n[0]).slice(0, 2).join('')}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 13 }}>{l.faculty_name}</div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{l.leave_date} — {l.leave_type}</div>
                    <div style={{ fontSize: 12, color: 'var(--text-secondary)', fontStyle: 'italic', marginTop: 2 }}>"{l.reason}"</div>
                  </div>
                  <span className="badge badge-amber">Pending</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="card" style={{ overflowY: 'auto', maxHeight: 480 }}>
          <h3 style={{ fontSize: 15, marginBottom: 14 }}>Faculty Workload</h3>
          <table>
            <thead><tr><th>Name</th><th>Subjects</th><th>Departments</th><th>Max Hrs</th><th>Status</th></tr></thead>
            <tbody>
              {faculty.map(f => (
                <tr key={f.id}>
                  <td><div className="flex gap-2"><div className="avatar" style={{ fontSize: 11, width: 28, height: 28 }}>{(f.name || 'U').split(' ').map(n => n[0]).slice(0, 2).join('')}</div><span style={{ fontSize: 13 }}>{f.name}</span></div></td>
                  <td><div className="chip-wrap">{f.subjects?.slice(0,2).map(s => <span key={s.id} className="chip" style={{ fontSize: 11 }}>{s.name}</span>)}{f.subjects?.length > 2 && <span className="chip chip-blue" style={{ fontSize: 11 }}>+{f.subjects.length - 2}</span>}</div></td>
                  <td><div className="chip-wrap">{[...new Set(f.grade_subjects?.map(g=>g.grade_name))].slice(0,3).map(g=>(<span key={g} className="chip chip-blue" style={{ fontSize: 11 }}>{g}</span>))}</div></td>
                  <td style={{ fontSize: 13 }}>{f.max_weekly_hours}h</td>
                  <td><span className={`badge ${f.is_present ? 'badge-green' : 'badge-rose'}`}>{f.is_present ? 'Present' : 'Absent'}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
