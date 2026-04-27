import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { RefreshCw } from 'lucide-react'
import api from '../../utils/api'


export default function FacDashboard() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [profile, setProfile] = useState(null)
  const [schedule, setSchedule] = useState([])
  const [leaves, setLeaves] = useState([])
  const [substitutions, setSubstitutions] = useState([])

  useEffect(() => {
    api.get('/faculty').then(r => {
      const me = r.data.find(f => f.email === user?.email || f.name === user?.name)
      setProfile(me)
    })
    api.get('/faculty/me/schedule').then(r => setSchedule(r.data)).catch(() => {})
    api.get('/leaves').then(r => setLeaves(r.data)).catch(() => {})
    api.get('/faculty/me/substitutions').then(r => setSubstitutions(r.data)).catch(() => {})
  }, [])

  const jsDay = new Date().getDay()
  const todayDay = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][jsDay]
  const todayClasses = schedule.filter(s => s.day === todayDay && !s.is_break && s.subject_name)
  const regularClasses = todayClasses.filter(s => !s.is_substitution)
  const subClasses = todayClasses.filter(s => s.is_substitution)

  const uniqueGrades = [...new Set(schedule.filter(s => s.grade_name).map(s => s.grade_name))]
  const myLeaves = leaves.filter(l => l.faculty_name === user?.name)

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Welcome, {user?.name?.split(' ')[0]}</h2>
        <p>Faculty Dashboard — your schedule and updates</p>
      </div>

      <div className="grid4" style={{ marginBottom: 20 }}>
        <div className="metric-card">
          <div className="metric-val">{profile?.subjects?.length || 0}</div>
          <div className="metric-lbl">Subjects</div>
        </div>
        <div className="metric-card">
          <div className="metric-val" style={{ color: 'var(--teal)' }}>{uniqueGrades.length}</div>
          <div className="metric-lbl">Classes</div>
        </div>
        <div className="metric-card">
          <div className="metric-val" style={{ color: 'var(--amber)' }}>{todayClasses.length}</div>
          <div className="metric-lbl">Classes today</div>
        </div>
        <div className="metric-card">
          <div className="metric-val" style={{ color: substitutions.length > 0 ? 'var(--amber)' : 'var(--green)' }}>{substitutions.length}</div>
          <div className="metric-lbl">Substitution duties</div>
        </div>
      </div>

      <div className="grid2">
        <div>
          {/* Today's classes */}
          <div className="card" style={{ marginBottom: 14 }}>
            <h3 style={{ fontSize: 15, marginBottom: 14 }}>Today's Classes ({todayDay})</h3>
            {todayClasses.length === 0 ? (
              <div className="empty-state" style={{ padding: 24 }}>No classes today.</div>
            ) : todayClasses.map((s, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: 12, padding: '11px 0',
                borderBottom: '1px solid var(--navy-border)'
              }}>
                <div style={{ width: 3, height: 36, background: s.is_substitution ? 'var(--amber)' : 'var(--teal)', borderRadius: 2, flexShrink: 0 }} />
                <div style={{ minWidth: 90, fontSize: 12, color: 'var(--text-muted)' }}>{s.slot_time}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: 13 }}>{s.subject_name}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-secondary)' }}>
                    {s.grade_name} · {s.room_id || '—'}
                    {s.is_substitution && (
                      <span style={{ color: 'var(--amber)', marginLeft: 6, fontWeight: 600 }}>
                        (covering for {s.original_faculty_name})
                      </span>
                    )}
                  </div>
                </div>
                <span className={`badge ${s.is_substitution ? 'badge-amber' : 'badge-teal'}`} style={{ fontSize: 11 }}>
                  {s.is_substitution ? 'Substitution' : 'Lecture'}
                </span>
              </div>
            ))}
            <button className="btn btn-ghost btn-sm" onClick={() => navigate('/faculty/schedule')} style={{ marginTop: 12, width: '100%', justifyContent: 'center' }}>
              View full schedule →
            </button>
          </div>

          {/* Substitution duties */}
          {substitutions.length > 0 && (
            <div className="card">
              <h3 style={{ fontSize: 15, marginBottom: 14, display: 'flex', alignItems: 'center', gap: 6 }}>
                <RefreshCw size={14} color="var(--amber)" /> Upcoming Substitution Duties
              </h3>
              {substitutions.map((s, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 0', borderBottom: '1px solid var(--navy-border)' }}>
                  <div style={{ width: 3, height: 32, borderRadius: 2, background: 'var(--amber)', flexShrink: 0 }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, fontWeight: 600 }}>{s.subject_name} · {s.department_name}</div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                      {s.day} {s.slot_time} · Leave date: {s.leave_date}
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', fontStyle: 'italic' }}>
                      Covering for {s.original_faculty_name}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Profile + Leaves */}
        <div>
          <div className="card" style={{ marginBottom: 14 }}>
            <h3 style={{ fontSize: 15, marginBottom: 14 }}>My Profile</h3>
            {profile && (
              <>
                <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 14 }}>
                  <div className="avatar" style={{ width: 44, height: 44, fontSize: 14 }}>
                    {profile.name?.split(' ').map(n=>n[0]).slice(0,2).join('')}
                  </div>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: 15 }}>{profile.name}</div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{profile.email}</div>
                    <span className={`badge ${profile.is_present ? 'badge-green' : 'badge-rose'}`} style={{ marginTop: 4 }}>
                      {profile.is_present ? 'Present' : 'On Leave'}
                    </span>
                  </div>
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 5 }}>Subjects</div>
                <div className="chip-wrap" style={{ marginBottom: 10 }}>
                  {profile.subjects?.map(s => <span key={s.id} className="chip" style={{ fontSize: 11 }}>{s.name}</span>)}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 5 }}>Department Assignments</div>
                <div className="chip-wrap">
                  {profile.grade_subjects?.map((gs, i) => (
                    <span key={i} className="chip chip-blue" style={{ fontSize: 11 }}>{gs.grade_name} · {gs.subject_name}</span>
                  ))}
                </div>
              </>
            )}
          </div>

          <div className="card">
            <div className="flex-between" style={{ marginBottom: 12 }}>
              <h3 style={{ fontSize: 15 }}>Recent Leaves</h3>
              <button className="btn btn-ghost btn-sm" onClick={() => navigate('/faculty/leave')}>Request leave</button>
            </div>
            {myLeaves.length === 0 ? (
              <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>No leave history.</div>
            ) : myLeaves.slice(0, 3).map(l => (
              <div key={l.id} className="flex-between" style={{ padding: '8px 0', borderBottom: '1px solid var(--navy-border)' }}>
                <div>
                  <div style={{ fontSize: 13 }}>{l.leave_date}</div>
                  <div style={{ fontSize: 12, color: 'var(--text-muted)', fontStyle: 'italic' }}>{l.reason}</div>
                </div>
                <span className={`badge ${l.status === 'approved' ? 'badge-green' : l.status === 'denied' ? 'badge-rose' : 'badge-amber'}`}>{l.status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
