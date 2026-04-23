import { useEffect, useState } from 'react'
import api from '../../utils/api'
import TimetableGrid from '../../components/TimetableGrid'

export default function TimetablePage() {
  const [all, setAll] = useState({})
  const [selGrade, setSelGrade] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/timetable').then(r => {
      setAll(r.data)
      const first = Object.keys(r.data)[0]
      if (first) setSelGrade(first)
    }).finally(() => setLoading(false))
  }, [])

  const gradeNames = Object.keys(all)
  const current = selGrade ? all[selGrade]?.days : null

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Timetable</h2>
        <p>Collision-free generated schedules per class</p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60 }}><div className="spinner" style={{ width: 30, height: 30 }} /></div>
      ) : gradeNames.length === 0 ? (
        <div className="card">
          <div className="empty-state">No timetables generated yet. Go to Generate to create one.</div>
        </div>
      ) : (
        <>
          <div className="tabs">
            {gradeNames.map(g => (
              <div key={g} className={`tab ${selGrade === g ? 'active' : ''}`} onClick={() => setSelGrade(g)}>{g}</div>
            ))}
          </div>
          <div className="card" style={{ overflowX: 'auto' }}>
            <TimetableGrid data={current} />
          </div>
        </>
      )}
    </div>
  )
}
