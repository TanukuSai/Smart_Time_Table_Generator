import { useEffect, useState } from 'react'
import { Wand2, Shield, CheckCircle, XCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import api from '../../utils/api'
import toast from 'react-hot-toast'

export default function GeneratePage() {
  const [departments, setGrades] = useState([])
  const [selGrades, setSelGrades] = useState([])
  const [constraints, setConstraints] = useState([])
  const [opts, setOpts] = useState({ slots_per_day: 6, start_time: "08:00", class_duration: 45, break_duration: 45, working_days: 6 })
  const [log, setLog] = useState('Awaiting generation...')
  const [loading, setLoading] = useState(false)
  const [generated, setGenerated] = useState(false)
  const [historyId, setHistoryId] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    api.get('/departments').then(r => setGrades(r.data))
    api.get('/constraints').then(r => setConstraints(r.data)).catch(() => {})
  }, [])

  const toggleGrade = (id) => setSelGrades(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])

  const generate = async () => {
    if (selGrades.length === 0) { toast.error('Select at least one department'); return }
    setLoading(true)
    setLog('[CSP] Starting...\n')
    setGenerated(false)
    setHistoryId(null)
    try {
      const { data } = await api.post('/timetable/generate', { department_ids: selGrades, ...opts })
      setLog(data.log.join('\n'))
      setGenerated(true)
      setHistoryId(data.history_id)
      toast.success('Timetable generated as draft — review & publish below!', { duration: 4000 })
    } catch (e) {
      toast.error('Generation failed')
      setLog('Error: ' + (e.response?.data?.detail || e.message))
    } finally { setLoading(false) }
  }

  const enabledConstraints = constraints.filter(c => c.is_enabled)
  const disabledConstraints = constraints.filter(c => !c.is_enabled)

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Generate Timetable</h2>
        <p>Configure parameters, review active constraints, and run the CSP scheduling algorithm</p>
      </div>

      <div className="grid2" style={{ alignItems: 'start' }}>
        <div>
          {/* Department selection */}
          <div className="card" style={{ marginBottom: 16 }}>
            <h3 style={{ fontSize: 15, marginBottom: 14 }}>Select Departments</h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 14 }}>
              {departments.map(g => (
                <button key={g.id} onClick={() => toggleGrade(g.id)} className="btn btn-sm"
                  style={{
                    background: selGrades.includes(g.id) ? 'rgba(245,158,11,0.2)' : 'transparent',
                    color: selGrades.includes(g.id) ? 'var(--amber)' : 'var(--text-muted)',
                    border: `1px solid ${selGrades.includes(g.id) ? 'rgba(245,158,11,0.4)' : 'var(--navy-border)'}`,
                    fontFamily: 'var(--font-display)', fontWeight: 700
                  }}>{g.name}</button>
              ))}
              <button onClick={() => setSelGrades(departments.map(g => g.id))} className="btn btn-ghost btn-sm">Select All</button>
              <button onClick={() => setSelGrades([])} className="btn btn-ghost btn-sm">Clear</button>
            </div>

            <label>Slots per Day</label>
            <input type="number" min="1" max="15" value={opts.slots_per_day} onChange={e => setOpts(p => ({...p, slots_per_day: parseInt(e.target.value)}))} />

            <div className="grid2" style={{ marginTop: 10 }}>
              <div>
                <label>College Start Time</label>
                <input type="time" value={opts.start_time} onChange={e => setOpts(p => ({...p, start_time: e.target.value}))} />
              </div>
              <div>
                <label>Class Duration (mins)</label>
                <input type="number" min="15" value={opts.class_duration} onChange={e => setOpts(p => ({...p, class_duration: parseInt(e.target.value)}))} />
              </div>
            </div>
            
            <div className="grid2" style={{ marginTop: 10 }}>
              <div>
                <label>Break Duration (mins)</label>
                <input type="number" min="0" value={opts.break_duration} onChange={e => setOpts(p => ({...p, break_duration: parseInt(e.target.value)}))} />
              </div>
              <div>
                <label>Working Days (1-7)</label>
                <input type="number" min="1" max="7" value={opts.working_days} onChange={e => setOpts(p => ({...p, working_days: parseInt(e.target.value)}))} />
              </div>
            </div>
          </div>

          {/* Active constraints summary */}
          <div className="card" style={{ marginBottom: 16 }}>
            <div className="flex-between" style={{ marginBottom: 14 }}>
              <h3 style={{ fontSize: 15, display: 'flex', alignItems: 'center', gap: 8 }}>
                <Shield size={15} color="var(--teal)" /> Active Constraints
              </h3>
              <button className="btn btn-ghost btn-sm" onClick={() => navigate('/admin/constraints')}>
                Manage →
              </button>
            </div>

            {enabledConstraints.map(c => (
              <div key={c.id} style={{
                display: 'flex', alignItems: 'center', gap: 10, padding: '8px 0',
                borderBottom: '1px solid var(--navy-border)', fontSize: 13
              }}>
                <CheckCircle size={14} color="var(--green)" style={{ flexShrink: 0 }} />
                <span style={{ flex: 1 }}>{c.name}</span>
                <span className={`badge ${c.type === 'hard' ? 'badge-rose' : 'badge-amber'}`} style={{ fontSize: 10 }}>{c.type}</span>
              </div>
            ))}

            {disabledConstraints.length > 0 && (
              <div style={{ marginTop: 10 }}>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>Disabled:</div>
                {disabledConstraints.map(c => (
                  <div key={c.id} style={{
                    display: 'flex', alignItems: 'center', gap: 10, padding: '6px 0',
                    fontSize: 12, color: 'var(--text-muted)'
                  }}>
                    <XCircle size={13} style={{ flexShrink: 0, opacity: 0.5 }} />
                    <span style={{ textDecoration: 'line-through' }}>{c.name}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <button className="btn btn-primary" onClick={generate} disabled={loading}
            style={{ width: '100%', justifyContent: 'center', padding: '12px' }}>
            {loading
              ? <><span className="spinner" style={{ width: 15, height: 15 }} /> Generating...</>
              : <><Wand2 size={15} /> Run CSP Algorithm</>}
          </button>

          {generated && (
            <div style={{ marginTop: 12 }}>
              <div className="alert alert-warn" style={{ marginBottom: 10 }}>
                <Wand2 size={14} style={{ flexShrink: 0 }} />
                <span>Draft saved! Review the timetable and publish when ready.</span>
              </div>
              <button className="btn btn-success" onClick={() => navigate('/admin/history')}
                style={{ width: '100%', justifyContent: 'center', padding: '12px' }}>
                <CheckCircle size={15} /> Review & Publish →
              </button>
            </div>
          )}
        </div>

        {/* Algorithm log */}
        <div className="card">
          <div className="flex-between" style={{ marginBottom: 14 }}>
            <h3 style={{ fontSize: 15 }}>Algorithm Log</h3>
            <button className="btn btn-ghost btn-sm" onClick={() => { setLog('Awaiting generation...'); setGenerated(false) }}>Clear</button>
          </div>
          <div className="log-output">{log}</div>
          <div className="alert alert-info" style={{ marginTop: 14 }}>
            <Wand2 size={14} style={{ flexShrink: 0 }} />
            <span>The CSP engine enforces all active constraints <strong>globally across all selected departments</strong>. Generated timetables are saved as <strong>drafts</strong> — review and publish from the History page.</span>
          </div>
        </div>
      </div>
    </div>
  )
}
