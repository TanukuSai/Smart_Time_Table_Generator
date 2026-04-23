import { useEffect, useState } from 'react'
import { Send, UserCheck, AlertTriangle, RefreshCw } from 'lucide-react'
import api from '../../utils/api'
import toast from 'react-hot-toast'

const STATUS_BADGE = { pending: 'badge-amber', approved: 'badge-green', denied: 'badge-rose' }

export default function FacLeave() {
  const [leaves, setLeaves] = useState([])
  const [form, setForm] = useState({ leave_date: '', reason: '', leave_type: 'casual' })
  const [saving, setSaving] = useState(false)

  const load = () => { api.get('/leaves').then(r => setLeaves(r.data)).catch(() => {}) }
  useEffect(() => { load() }, [])

  const handleSubmit = async () => {
    if (!form.leave_date || !form.reason) { toast.error('Fill in all fields'); return }
    setSaving(true)
    try {
      await api.post('/leaves', form)
      toast.success('Leave request submitted!')
      setForm({ leave_date: '', reason: '', leave_type: 'casual' })
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    } finally { setSaving(false) }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Leave Requests</h2>
        <p>Apply for leave — the admin will review and notify you</p>
      </div>

      <div className="grid2" style={{ alignItems: 'start' }}>
        <div className="card">
          <h3 style={{ fontSize: 15, marginBottom: 18 }}>Apply for Leave</h3>

          <label>Leave Date *</label>
          <input type="date" value={form.leave_date} onChange={e => setForm(p => ({...p, leave_date: e.target.value}))} />

          <label>Leave Type</label>
          <select value={form.leave_type} onChange={e => setForm(p => ({...p, leave_type: e.target.value}))}>
            <option value="casual">Casual Leave</option>
            <option value="medical">Medical Leave</option>
            <option value="personal">Personal Leave</option>
            <option value="conference">Conference / Workshop</option>
            <option value="emergency">Emergency</option>
          </select>

          <label>Reason *</label>
          <textarea rows={4} placeholder="Briefly describe the reason for your leave..." value={form.reason} onChange={e => setForm(p => ({...p, reason: e.target.value}))} />

          <div className="alert alert-warn" style={{ marginTop: 14 }}>
            <span style={{ fontSize: 13 }}>Note: Your leave will automatically flag affected departments for substitution planning. The admin will review and notify you.</span>
          </div>

          <button className="btn btn-primary" onClick={handleSubmit} disabled={saving} style={{ marginTop: 14, width: '100%', justifyContent: 'center' }}>
            {saving ? <><span className="spinner" style={{ width: 14, height: 14 }} /> Submitting...</> : <><Send size={14} /> Submit Request</>}
          </button>
        </div>

        <div className="card">
          <h3 style={{ fontSize: 15, marginBottom: 16 }}>My Leave History</h3>
          {leaves.length === 0 ? (
            <div className="empty-state" style={{ padding: 28 }}>No leave requests yet.</div>
          ) : leaves.map(l => (
            <div key={l.id} style={{ padding: '12px 0', borderBottom: '1px solid var(--navy-border)' }}>
              <div className="flex-between" style={{ marginBottom: 4 }}>
                <div style={{ fontWeight: 600, fontSize: 13 }}>{l.leave_date}</div>
                <span className={`badge ${STATUS_BADGE[l.status]}`}>{l.status}</span>
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'capitalize', marginBottom: 3 }}>{l.leave_type} leave</div>
              <div style={{ fontSize: 13, color: 'var(--text-secondary)', fontStyle: 'italic' }}>"{l.reason}"</div>
              {l.admin_note && (
                <div style={{ fontSize: 12, color: 'var(--teal)', marginTop: 6 }}>
                  Admin: "{l.admin_note}"
                </div>
              )}

              {/* Show who covers your slots for approved leaves */}
              {l.status === 'approved' && l.substitutions?.length > 0 && (
                <div style={{
                  marginTop: 10, padding: '10px 12px',
                  background: 'rgba(16,185,129,0.06)',
                  border: '1px solid rgba(16,185,129,0.15)',
                  borderRadius: 'var(--radius-md)'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8, fontWeight: 600, fontSize: 12, color: 'var(--green)' }}>
                    <RefreshCw size={12} /> Your classes are covered:
                  </div>
                  {l.substitutions.map((s, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '5px 0', fontSize: 12, borderBottom: i < l.substitutions.length - 1 ? '1px solid rgba(16,185,129,0.1)' : 'none' }}>
                      <span style={{ color: 'var(--amber)', fontWeight: 600, minWidth: 30 }}>{s.day}</span>
                      <span style={{ color: 'var(--text-muted)', minWidth: 70 }}>{s.slot_time || `Slot ${s.slot_index + 1}`}</span>
                      <span style={{ fontWeight: 600 }}>{s.subject_name}</span>
                      <span style={{ color: 'var(--text-muted)' }}>→</span>
                      {s.substitute_faculty_name ? (
                        <span style={{ display: 'flex', alignItems: 'center', gap: 3, color: 'var(--green)', fontWeight: 600 }}>
                          <UserCheck size={11} /> {s.substitute_faculty_name}
                        </span>
                      ) : (
                        <span style={{ display: 'flex', alignItems: 'center', gap: 3, color: 'var(--rose)' }}>
                          <AlertTriangle size={11} /> No substitute
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {l.status === 'approved' && (!l.substitutions || l.substitutions.length === 0) && (
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6, fontStyle: 'italic' }}>
                  No timetable slots on this date.
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
