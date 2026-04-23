import { useEffect, useState } from 'react'
import { RefreshCw, UserCheck } from 'lucide-react'
import api from '../../utils/api'

export default function StuFacultyToday() {
  const [faculty, setFaculty] = useState([])
  const [loading, setLoading] = useState(true)
  const [timetable, setTimetable] = useState({})

  useEffect(() => {
    api.get('/faculty').then(r => setFaculty(r.data)).finally(() => setLoading(false))
    api.get('/timetable').then(r => setTimetable(r.data)).catch(() => {})
  }, [])

  const present = faculty.filter(f => f.is_present)
  const absent = faculty.filter(f => !f.is_present)

  // Extract today's substitutions from timetable data
  const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
  const todayDay = DAYS[new Date().getDay() - 1] || 'Mon'
  const todaySubs = []
  let hasClassesToday = false

  Object.entries(timetable).forEach(([deptName, dept]) => {
    const daySlots = dept?.days?.[todayDay] || []
    
    // Check if there's any actual class today
    if (daySlots.some(slot => !slot.is_break && slot.subject_name)) {
      hasClassesToday = true
    }

    daySlots.forEach(slot => {
      if (slot.is_substituted) {
        todaySubs.push({ ...slot, department_name: deptName })
      }
    })
  })

  const FacultyCard = ({ f }) => (
    <div style={{
      background: 'var(--surface-raised)',
      border: '1px solid var(--navy-border)',
      borderRadius: 'var(--radius-md)',
      padding: '14px 16px',
      display: 'flex', alignItems: 'flex-start', gap: 12
    }}>
      <div className={`avatar ${f.is_present ? '' : 'avatar-rose'}`} style={{ fontSize: 11 }}>
        {f.name?.split(' ').map(n => n[0]).slice(0, 2).join('')}
      </div>
      <div style={{ flex: 1 }}>
        <div className="flex-between" style={{ marginBottom: 4 }}>
          <div style={{ fontWeight: 600, fontSize: 14 }}>{f.name}</div>
          <span className={`badge ${f.is_present ? 'badge-green' : 'badge-rose'}`}>{f.is_present ? 'Present' : 'On Leave'}</span>
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 6 }}>{f.employee_code}</div>
        <div className="chip-wrap" style={{ marginBottom: 5 }}>
          {f.subjects?.map(s => <span key={s.id} className="chip" style={{ fontSize: 11 }}>{s.name}</span>)}
        </div>
        <div className="chip-wrap">
          {[...new Set(f.grade_subjects?.map(g=>g.grade_name))].map(g => (
            <span key={g} className="chip chip-blue" style={{ fontSize: 11 }}>{g}</span>
          ))}
        </div>
      </div>
    </div>
  )

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Faculty Today</h2>
        <p>See which faculty members are present and their classes</p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60 }}><div className="spinner" style={{ width: 28, height: 28 }} /></div>
      ) : faculty.length === 0 ? (
        <div className="card"><div className="empty-state">No faculty information available.</div></div>
      ) : !hasClassesToday && Object.keys(timetable).length > 0 ? (
        <div className="card">
          <div className="empty-state" style={{ padding: '60px 20px' }}>
            <h3 style={{ fontSize: 20, marginBottom: 8 }}>🎉 It's a holiday!</h3>
            <p style={{ color: 'var(--text-muted)' }}>You have no classes scheduled for {todayDay}. Enjoy your day off!</p>
          </div>
        </div>
      ) : (
        <>
          {/* Today's substitutions banner */}
          {todaySubs.length > 0 && (
            <div className="card" style={{ marginBottom: 20, background: 'rgba(245,158,11,0.04)', border: '1px solid rgba(245,158,11,0.15)' }}>
              <h3 style={{ fontSize: 14, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6, color: 'var(--amber)' }}>
                <RefreshCw size={14} /> Today's Substitutions ({todayDay})
              </h3>
              {todaySubs.map((s, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '7px 0', fontSize: 13, borderBottom: i < todaySubs.length - 1 ? '1px solid rgba(245,158,11,0.1)' : 'none' }}>
                  <span style={{ fontWeight: 600, minWidth: 60 }}>{s.slot_time?.split('–')[0]}</span>
                  <span>{s.subject_name}</span>
                  <span style={{ color: 'var(--text-muted)' }}>({s.department_name})</span>
                  <span style={{ color: 'var(--text-muted)' }}>—</span>
                  <span style={{ color: 'var(--text-muted)', textDecoration: 'line-through' }}>{s.original_faculty_name}</span>
                  <span style={{ color: 'var(--text-muted)' }}>→</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 3, color: 'var(--green)', fontWeight: 600 }}>
                    <UserCheck size={12} /> {s.substitute_faculty_name || s.faculty_name}
                  </span>
                </div>
              ))}
            </div>
          )}

          <div style={{ marginBottom: 24 }}>
            <h3 style={{ fontSize: 14, color: 'var(--green)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--green)', display: 'inline-block' }} />
              Present ({present.length})
            </h3>
            <div className="grid2">
              {present.map(f => <FacultyCard key={f.id} f={f} />)}
            </div>
          </div>

          {absent.length > 0 && (
            <div>
              <h3 style={{ fontSize: 14, color: 'var(--rose)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--rose)', display: 'inline-block' }} />
                On Leave ({absent.length})
              </h3>
              <div className="grid2">
                {absent.map(f => <FacultyCard key={f.id} f={f} />)}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
