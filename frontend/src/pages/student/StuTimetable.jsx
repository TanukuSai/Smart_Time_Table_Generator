import { useEffect, useState } from 'react'
import api from '../../utils/api'
import TimetableGrid from '../../components/TimetableGrid'
import { useAuth } from '../../context/AuthContext'

export default function StuTimetable() {
  const [all, setAll] = useState({})
  const [loading, setLoading] = useState(true)
  const { user } = useAuth()

  useEffect(() => {
    api.get('/timetable').then(r => {
      setAll(r.data)
    }).finally(() => setLoading(false))
  }, [])

  // Student sees only their department (backend already filters)
  const departments = Object.keys(all)
  const deptName = departments[0] || null
  const current = deptName ? all[deptName]?.days : null

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>My Class Timetable</h2>
        <p>{deptName ? `Schedule for ${deptName}` : 'View your class schedule — read only'}</p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60 }}><div className="spinner" style={{ width: 28, height: 28 }} /></div>
      ) : !current ? (
        <div className="card"><div className="empty-state">No timetable available for your class yet. Please contact your admin.</div></div>
      ) : (
        <div className="card" style={{ overflowX: 'auto' }}>
          {deptName && (
            <div style={{ marginBottom: 14, display: 'flex', alignItems: 'center', gap: 10 }}>
              <span className="badge badge-amber" style={{ fontSize: 12, padding: '4px 12px' }}>{deptName}</span>
            </div>
          )}
          <TimetableGrid data={current} />
        </div>
      )}
    </div>
  )
}
