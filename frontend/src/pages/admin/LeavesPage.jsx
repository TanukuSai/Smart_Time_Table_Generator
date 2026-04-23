import { useEffect, useState } from 'react'
import { CheckCircle, XCircle, RefreshCw, UserCheck, AlertTriangle, ExternalLink } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import api from '../../utils/api'
import toast from 'react-hot-toast'

const STATUS_BADGE = { pending: 'badge-amber', approved: 'badge-green', denied: 'badge-rose' }

export default function LeavesPage() {
  const [leaves, setLeaves] = useState([])
  const [tab, setTab] = useState('pending')
  const [note, setNote] = useState({})
  const [reviewing, setReviewing] = useState(null)
  const [substitutions, setSubstitutions] = useState([])
  const navigate = useNavigate()

  const load = () => {
    api.get('/leaves').then(r => setLeaves(r.data)).catch(console.error)
    api.get('/leaves/substitutions').then(r => setSubstitutions(r.data)).catch(() => {})
  }
  useEffect(() => { load() }, [])

  const review = async (id, status) => {
    setReviewing(id)
    try {
      const { data } = await api.patch(`/leaves/${id}/review`, { status, admin_note: note[id] || null })
      if (status === 'approved' && data.substitutions?.length > 0) {
        const assigned = data.substitutions.filter(s => s.status === 'auto_assigned').length
        toast.success(`Leave approved — ${assigned} substitutes assigned! Review the draft in History.`, { duration: 5000 })
      } else if (status === 'approved') {
        toast.success('Leave approved (no timetable slots to substitute)')
      } else {
        toast.success(`Leave ${status}`)
      }
      load()
    } catch {
      toast.error('Failed to review leave')
    } finally {
      setReviewing(null)
    }
  }

  const tabs = ['pending', 'approved', 'denied', 'substitutions']
  const filtered = tab === 'substitutions' ? [] : leaves.filter(l => l.status === tab)

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Leave Requests & Smart Substitution</h2>
        <p>Review leave applications — substitutes are auto-assigned on approval</p>
      </div>

      <div className="tabs">
        {tabs.map(s => (
          <div key={s} className={`tab ${tab === s ? 'active' : ''}`} onClick={() => setTab(s)}>
            {s === 'substitutions' ? `Substitutions (${substitutions.length})` :
              `${s.charAt(0).toUpperCase() + s.slice(1)} (${leaves.filter(l => l.status === s).length})`}
          </div>
        ))}
      </div>

      {/* ─── Substitutions tab ─── */}
      {tab === 'substitutions' && (
        <div className="card">
          {substitutions.length === 0 ? (
            <div className="empty-state">No active substitutions.</div>
          ) : (
            <table style={{ width: '100%', fontSize: 13 }}>
              <thead>
                <tr>
                  <th style={{ fontSize: 11 }}>Leave Date</th>
                  <th style={{ fontSize: 11 }}>Original Faculty</th>
                  <th style={{ fontSize: 11 }}>Day / Slot</th>
                  <th style={{ fontSize: 11 }}>Subject</th>
                  <th style={{ fontSize: 11 }}>Department</th>
                  <th style={{ fontSize: 11 }}>Substitute</th>
                  <th style={{ fontSize: 11 }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {substitutions.map((s, i) => (
                  <tr key={i}>
                    <td style={{ fontWeight: 600, whiteSpace: 'nowrap' }}>{s.leave_date}</td>
                    <td>{s.original_faculty_name || '—'}</td>
                    <td>
                      <span style={{ color: 'var(--amber)', fontWeight: 600 }}>{s.day}</span>
                      {' '}{s.slot_time || `Slot ${s.slot_index + 1}`}
                    </td>
                    <td>{s.subject_name || '—'}</td>
                    <td>{s.department_name || '—'}</td>
                    <td>
                      {s.substitute_faculty_name ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                          <UserCheck size={12} color="var(--green)" />
                          <span style={{ fontWeight: 600, color: 'var(--green)' }}>{s.substitute_faculty_name}</span>
                        </div>
                      ) : (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--rose)' }}>
                          <AlertTriangle size={12} /> Unfilled
                        </div>
                      )}
                    </td>
                    <td>
                      <span className={`badge ${s.status === 'auto_assigned' ? 'badge-green' : 'badge-rose'}`} style={{ fontSize: 10 }}>
                        {s.status === 'auto_assigned' ? 'Assigned' : 'Unfilled'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}

      {/* ─── Leave cards ─── */}
      {tab !== 'substitutions' && filtered.length === 0 && <div className="empty-state">No {tab} leave requests.</div>}

      {tab !== 'substitutions' && filtered.map(l => (
        <div key={l.id} className="leave-card" style={{ marginBottom: 12, alignItems: 'flex-start' }}>
          <div className="avatar avatar-teal" style={{ fontSize: 11, marginTop: 2 }}>
            {(l.faculty_name || 'U').split(' ').map(n => n[0]).slice(0, 2).join('')}
          </div>
          <div style={{ flex: 1 }}>
            <div className="flex-between" style={{ marginBottom: 4 }}>
              <div style={{ fontWeight: 600, fontSize: 14 }}>{l.faculty_name}</div>
              <span className={`badge ${STATUS_BADGE[l.status]}`}>{l.status}</span>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 4 }}>
              Date: <strong style={{ color: 'var(--text-secondary)' }}>{l.leave_date}</strong>
              &nbsp;·&nbsp; Type: <strong style={{ color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{l.leave_type}</strong>
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-secondary)', fontStyle: 'italic', marginBottom: 8 }}>"{l.reason}"</div>

            {l.affected_departments?.length > 0 && (
              <div style={{ marginBottom: 8 }}>
                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Affected departments: </span>
                <div className="chip-wrap" style={{ display: 'inline-flex', marginLeft: 4 }}>
                  {l.affected_departments.map(g => <span key={g} className="chip chip-blue" style={{ fontSize: 11 }}>{g}</span>)}
                </div>
              </div>
            )}

            {l.admin_note && (
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginBottom: 8 }}>
                Admin note: <em style={{ color: 'var(--text-secondary)' }}>{l.admin_note}</em>
              </div>
            )}

            {/* Substitution Results */}
            {l.status === 'approved' && l.substitutions?.length > 0 && (
              <div style={{
                marginTop: 10, marginBottom: 8, padding: '12px 14px',
                background: 'rgba(16,185,129,0.06)',
                border: '1px solid rgba(16,185,129,0.15)',
                borderRadius: 'var(--radius-md)'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 600, fontSize: 13, color: 'var(--green)' }}>
                    <RefreshCw size={13} /> Smart Substitution Results
                  </div>
                  <button className="btn btn-ghost btn-sm" onClick={() => navigate('/admin/history')}
                    style={{ fontSize: 11, color: 'var(--amber)' }}>
                    <ExternalLink size={11} /> Review Draft
                  </button>
                </div>
                <table style={{ width: '100%', fontSize: 12 }}>
                  <thead>
                    <tr>
                      <th style={{ fontSize: 11 }}>Slot</th>
                      <th style={{ fontSize: 11 }}>Subject</th>
                      <th style={{ fontSize: 11 }}>Department</th>
                      <th style={{ fontSize: 11 }}>Substitute</th>
                      <th style={{ fontSize: 11 }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {l.substitutions.map((s, i) => (
                      <tr key={i}>
                        <td style={{ whiteSpace: 'nowrap' }}>
                          <span style={{ color: 'var(--amber)', fontWeight: 600 }}>{s.day}</span> {s.slot_time || `Slot ${s.slot_index + 1}`}
                        </td>
                        <td>{s.subject_name || '—'}</td>
                        <td>{s.department_name || '—'}</td>
                        <td>
                          {s.substitute_faculty_name ? (
                            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                              <UserCheck size={12} color="var(--green)" />
                              <span style={{ fontWeight: 600, color: 'var(--green)' }}>{s.substitute_faculty_name}</span>
                            </div>
                          ) : (
                            <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--rose)' }}>
                              <AlertTriangle size={12} /> No substitute
                            </div>
                          )}
                        </td>
                        <td>
                          <span className={`badge ${s.status === 'auto_assigned' ? 'badge-green' : 'badge-rose'}`} style={{ fontSize: 10 }}>
                            {s.status === 'auto_assigned' ? 'Assigned' : 'Unfilled'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 8 }}>
                  {l.substitutions.filter(s => s.status === 'auto_assigned').length} of {l.substitutions.length} slots filled automatically
                </div>
              </div>
            )}

            {l.status === 'approved' && (!l.substitutions || l.substitutions.length === 0) && (
              <div style={{
                fontSize: 12, color: 'var(--text-muted)', marginTop: 8, padding: '8px 12px',
                background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.15)',
                borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', gap: 6
              }}>
                <RefreshCw size={12} /> No timetable slots found for this faculty on {l.leave_date}
              </div>
            )}

            {l.status === 'pending' && (
              <div>
                <input placeholder="Optional note to faculty..." value={note[l.id] || ''} onChange={e => setNote(p => ({...p, [l.id]: e.target.value}))}
                  style={{ marginBottom: 10 }} />
                <div className="flex gap-2">
                  <button className="btn btn-success btn-sm" onClick={() => review(l.id, 'approved')} disabled={reviewing === l.id}>
                    {reviewing === l.id
                      ? <><span className="spinner" style={{ width: 12, height: 12 }} /> Finding substitutes...</>
                      : <><CheckCircle size={13} /> Approve & Auto-Substitute</>}
                  </button>
                  <button className="btn btn-danger btn-sm" onClick={() => review(l.id, 'denied')} disabled={reviewing === l.id}>
                    <XCircle size={13} /> Deny
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
