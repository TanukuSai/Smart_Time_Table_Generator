import { useEffect, useState } from 'react'
import api from '../../utils/api'

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
const TIMES_COUNT = 7

export default function FacSchedule() {
  const [schedule, setSchedule] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/faculty/me/schedule').then(r => setSchedule(r.data)).finally(() => setLoading(false))
  }, [])

  const getSlot = (day, idx) => schedule.find(s => s.day === day && s.slot_index === idx)

  if (loading) return <div style={{ textAlign: 'center', padding: 60 }}><div className="spinner" style={{ width: 28, height: 28 }} /></div>

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>My Weekly Schedule</h2>
        <p>Your personalised timetable — substitution duties highlighted in amber</p>
      </div>

      {/* Calendar style */}
      <div className="cal-grid" style={{ marginBottom: 24 }}>
        {DAYS.map(day => (
          <div key={day} className="cal-day">
            <div className="cal-day-head">{day}</div>
            {Array.from({ length: TIMES_COUNT }).map((_, i) => {
              const s = getSlot(day, i)
              if (!s) return <div key={i} className="cal-slot cal-slot-free">Free</div>
              if (s.is_break) return <div key={i} className="cal-slot cal-slot-break">Break</div>
              if (!s.subject_name) return <div key={i} className="cal-slot cal-slot-free">Free</div>
              const isSub = s.is_substitution
              return (
                <div key={i} className="cal-slot cal-slot-class" style={isSub ? {
                  borderLeft: '3px solid var(--amber)',
                  background: 'rgba(245,158,11,0.1)'
                } : {}}>
                  <div style={{ fontWeight: 600, fontSize: 11.5, color: isSub ? 'var(--amber)' : 'var(--amber-light)' }}>{s.subject_name}</div>
                  <div style={{ fontSize: 10.5, color: 'var(--text-secondary)', marginTop: 2 }}>
                    {isSub ? `Sub for ${s.original_faculty_name}` : `Class ${s.grade_name}`}
                  </div>
                  <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{s.slot_time?.split('–')[0]}</div>
                  {isSub && <div style={{ fontSize: 9, color: 'var(--amber)', fontWeight: 700, marginTop: 2 }}>SUBSTITUTION</div>}
                </div>
              )
            })}
          </div>
        ))}
      </div>

      {/* Full table */}
      <div className="card" style={{ overflowX: 'auto' }}>
        <h3 style={{ fontSize: 15, marginBottom: 14 }}>Detailed View</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '90px repeat(5,1fr)', gap: 1, background: 'var(--navy-border)', borderRadius: 10, overflow: 'hidden' }}>
          <div className="tt-cell tt-head">Slot</div>
          {DAYS.map(d => <div key={d} className="tt-cell tt-head" style={{ textAlign: 'center' }}>{d}</div>)}
          {Array.from({ length: TIMES_COUNT }).map((_, i) => {
            const sample = DAYS.map(d => getSlot(d, i)).find(Boolean)
            return (
              <div key={i} style={{ display: 'contents' }}>
                <div className="tt-cell tt-head" style={{ fontSize: 10.5 }}>{sample?.slot_time || ''}</div>
                {DAYS.map(day => {
                  const s = getSlot(day, i)
                  if (!s) return <div key={day} className="tt-cell" style={{ opacity: 0.3 }} />
                  if (s.is_break) return <div key={day} className="tt-cell tt-break">Break</div>
                  if (!s.subject_name) return <div key={day} className="tt-cell" style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: 11 }}>Free</div>
                  const isSub = s.is_substitution
                  return (
                    <div key={day} className="tt-cell tt-slot-fac-class" style={isSub ? { borderLeft: '3px solid var(--amber)', background: 'rgba(245,158,11,0.06)' } : {}}>
                      <div className="tt-slot-sub" style={{ color: isSub ? 'var(--amber)' : 'var(--teal)' }}>{s.subject_name}</div>
                      <div className="tt-slot-fac">
                        {isSub ? `Sub for ${s.original_faculty_name}` : `Class ${s.grade_name}`}
                      </div>
                      <div className="tt-slot-room">{s.room_id || '—'}</div>
                      {isSub && <div style={{ fontSize: 9, color: 'var(--amber)', fontWeight: 700 }}>SUB</div>}
                    </div>
                  )
                })}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
