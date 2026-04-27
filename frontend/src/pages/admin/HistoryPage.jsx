import { useEffect, useState } from 'react'
import { History, Trash2, ChevronDown, ChevronRight, CalendarDays, CheckCircle, Send, Edit3, X, RefreshCw } from 'lucide-react'
import api from '../../utils/api'
import toast from 'react-hot-toast'

const STATUS_STYLE = {
  draft: { label: 'Draft', cls: 'badge-amber' },
  published: { label: 'Published', cls: 'badge-green' },
  archived: { label: 'Archived', cls: 'badge-slate' }
}
const TYPE_STYLE = {
  regular: { label: 'Regular', cls: 'badge-teal' },
  substitution: { label: 'Substitution', cls: 'badge-rose' }
}

export default function HistoryPage() {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [expanded, setExpanded] = useState(null)
  const [snapshot, setSnapshot] = useState(null)
  const [snapshotLoading, setSnapshotLoading] = useState(false)
  const [selDept, setSelDept] = useState(null)
  const [publishing, setPublishing] = useState(null)
  const [editingSlot, setEditingSlot] = useState(null) // { historyId, dept, day, slotIndex, faculty, subject }
  const [faculty, setFaculty] = useState([])
  const [subjects, setSubjects] = useState([])

  useEffect(() => {
    loadHistory()
    api.get('/faculty').then(r => setFaculty(r.data)).catch(() => {})
    api.get('/subjects').then(r => setSubjects(r.data)).catch(() => {})
  }, [])

  const loadHistory = () => {
    setLoading(true)
    api.get('/timetable/history').then(r => setEntries(r.data)).catch(() => {}).finally(() => setLoading(false))
  }

  const toggleExpand = async (id) => {
    if (expanded === id) {
      setExpanded(null); setSnapshot(null); setSelDept(null); return
    }
    setExpanded(id)
    setSnapshotLoading(true)
    try {
      const { data } = await api.get(`/timetable/history/${id}`)
      const snap = typeof data.snapshot === 'string' ? JSON.parse(data.snapshot) : data.snapshot
      setSnapshot(snap)
      const depts = Object.keys(snap)
      if (depts.length > 0) setSelDept(depts[0])
    } catch {
      toast.error('Failed to load snapshot')
    } finally {
      setSnapshotLoading(false)
    }
  }

  const publishDraft = async (id, e) => {
    e.stopPropagation()
    setPublishing(id)
    try {
      await api.post(`/timetable/history/${id}/publish`)
      toast.success('Timetable published and now live!', { duration: 4000 })
      loadHistory()
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to publish')
    } finally {
      setPublishing(null)
    }
  }

  const deleteEntry = async (id, e) => {
    e.stopPropagation()
    if (!confirm('Delete this history entry?')) return
    try {
      await api.delete(`/timetable/history/${id}`)
      toast.success('Deleted')
      if (expanded === id) { setExpanded(null); setSnapshot(null) }
      loadHistory()
    } catch {
      toast.error('Failed to delete')
    }
  }

  const startEdit = (historyId, dept, day, slot) => {
    setEditingSlot({
      historyId, dept, day,
      slotIndex: slot.slot_index,
      faculty: slot.faculty || '',
      subject: slot.subject || ''
    })
  }

  const saveEdit = async () => {
    if (!editingSlot) return
    try {
      const { data } = await api.patch(`/timetable/history/${editingSlot.historyId}/slot`, {
        department_name: editingSlot.dept,
        day: editingSlot.day,
        slot_index: editingSlot.slotIndex,
        faculty_name: editingSlot.faculty || null,
        subject_name: editingSlot.subject || null
      })
      const snap = typeof data.snapshot === 'string' ? JSON.parse(data.snapshot) : data.snapshot
      setSnapshot(snap)
      toast.success('Slot updated')
      setEditingSlot(null)
    } catch {
      toast.error('Failed to update slot')
    }
  }

  const formatDate = (ts) => {
    if (!ts) return '—'
    const d = new Date(ts)
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) +
      ' ' + d.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Timetable History</h2>
        <p>Review drafts, edit slots, and publish timetables</p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 60 }}><div className="spinner" style={{ width: 28, height: 28 }} /></div>
      ) : entries.length === 0 ? (
        <div className="card">
          <div className="empty-state">
            <History size={32} style={{ opacity: 0.3, marginBottom: 12 }} />
            <div>No generation history yet. Generate a timetable first.</div>
          </div>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {entries.map(entry => {
            const isExpanded = expanded === entry.id
            const deptIds = typeof entry.department_ids === 'string' ? JSON.parse(entry.department_ids) : entry.department_ids
            const st = STATUS_STYLE[entry.status] || STATUS_STYLE.draft
            const tp = TYPE_STYLE[entry.type] || TYPE_STYLE.regular
            const isDraft = entry.status === 'draft'
            return (
              <div key={entry.id} className="card" style={{ padding: 0, overflow: 'hidden' }}>
                {/* Header row */}
                <div onClick={() => toggleExpand(entry.id)} style={{
                  padding: '14px 18px', cursor: 'pointer',
                  display: 'flex', alignItems: 'center', gap: 12,
                  borderBottom: isExpanded ? '1px solid var(--navy-border)' : 'none',
                  transition: 'background 150ms',
                }}>
                  {isExpanded ? <ChevronDown size={16} color="var(--amber)" /> : <ChevronRight size={16} color="var(--text-muted)" />}
                  <CalendarDays size={16} color="var(--amber)" style={{ flexShrink: 0 }} />
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: 14, display: 'flex', alignItems: 'center', gap: 8 }}>
                      {entry.name}
                      <span className={`badge ${st.cls}`} style={{ fontSize: 10 }}>{st.label}</span>
                      <span className={`badge ${tp.cls}`} style={{ fontSize: 10 }}>{tp.label}</span>
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                      {formatDate(entry.generated_at)} · {deptIds?.length || 0} departments
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: 6 }} onClick={e => e.stopPropagation()}>
                    {isDraft && (
                      <button className="btn btn-success btn-sm" onClick={(e) => publishDraft(entry.id, e)}
                        disabled={publishing === entry.id} style={{ fontSize: 12 }}>
                        {publishing === entry.id
                          ? <><span className="spinner" style={{ width: 12, height: 12 }} /> Publishing...</>
                          : <><Send size={12} /> Publish</>}
                      </button>
                    )}
                    <button className="btn btn-ghost btn-sm" onClick={(e) => deleteEntry(entry.id, e)}
                      style={{ color: 'var(--rose)' }}>
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>

                {/* Expanded body */}
                {isExpanded && (
                  <div style={{ padding: '16px 18px' }}>
                    {snapshotLoading ? (
                      <div style={{ textAlign: 'center', padding: 30 }}><div className="spinner" style={{ width: 22, height: 22 }} /></div>
                    ) : snapshot ? (
                      <>
                        {isDraft && (
                          <div className="alert alert-warn" style={{ marginBottom: 14 }}>
                            <Edit3 size={14} style={{ flexShrink: 0 }} />
                            <span>This is a <strong>draft</strong>. Click any slot to edit, then publish when ready.</span>
                          </div>
                        )}

                        <div className="tabs" style={{ marginBottom: 14 }}>
                          {Object.keys(snapshot).map(dept => (
                            <div key={dept} className={`tab ${selDept === dept ? 'active' : ''}`}
                              onClick={() => setSelDept(dept)}>{dept}</div>
                          ))}
                        </div>
                        {selDept && snapshot[selDept] && (
                          <div style={{ overflowX: 'auto' }}>
                            <SnapshotGrid
                              data={snapshot[selDept]}
                              isDraft={isDraft}
                              historyId={entry.id}
                              dept={selDept}
                              editingSlot={editingSlot}
                              onStartEdit={(day, slot) => startEdit(entry.id, selDept, day, slot)}
                              onCancelEdit={() => setEditingSlot(null)}
                              editState={editingSlot}
                              setEditState={setEditingSlot}
                              onSaveEdit={saveEdit}
                              faculty={faculty}
                              subjects={subjects}
                            />
                          </div>
                        )}

                        {/* Log collapsible */}
                        {entry.log && (
                          <details style={{ marginTop: 14 }}>
                            <summary style={{ cursor: 'pointer', fontSize: 13, color: 'var(--text-muted)' }}>
                              View Algorithm Log
                            </summary>
                            <div className="log-output" style={{ marginTop: 8, maxHeight: 300, overflowY: 'auto' }}>
                              {entry.log}
                            </div>
                          </details>
                        )}
                      </>
                    ) : (
                      <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>No snapshot data available.</div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function SnapshotGrid({ data, isDraft, historyId, dept, editingSlot, onStartEdit, onCancelEdit, editState, setEditState, onSaveEdit, faculty, subjects }) {
  if (!data) return null
  const allDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
  const presentDays = allDays.filter(d => data[d] && data[d].length > 0)
  if (presentDays.length === 0) return <div style={{ color: 'var(--text-muted)', fontSize: 13 }}>No data for this department.</div>

  const maxSlots = Math.max(...presentDays.map(d => data[d].length))

  const isEditing = (day, slotIndex) =>
    editState && editState.historyId === historyId && editState.dept === dept && editState.day === day && editState.slotIndex === slotIndex

  return (
    <table>
      <thead>
        <tr>
          <th>Time</th>
          {presentDays.map(d => <th key={d}>{d}</th>)}
        </tr>
      </thead>
      <tbody>
        {Array.from({ length: maxSlots }, (_, i) => {
          const firstDay = presentDays.find(d => data[d][i])
          const slot = firstDay ? data[firstDay][i] : null
          const isBreak = slot?.is_break
          return (
            <tr key={i} style={isBreak ? { background: 'rgba(245,158,11,0.05)' } : {}}>
              <td style={{ fontSize: 11, color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                {slot?.slot_time || `Slot ${i + 1}`}
              </td>
              {presentDays.map(d => {
                const s = data[d]?.[i]
                if (!s) return <td key={d}>—</td>
                if (s.is_break) return <td key={d} style={{ textAlign: 'center', color: 'var(--amber)', fontSize: 12 }}>BREAK</td>

                const isSub = s.is_substitution
                const editing = isEditing(d, s.slot_index)

                if (editing) {
                  return (
                    <td key={d} style={{ padding: 6 }}>
                      <select value={editState.subject} onChange={e => setEditState(p => ({ ...p, subject: e.target.value }))}
                        style={{ fontSize: 11, marginBottom: 4, width: '100%', padding: '4px 6px' }}>
                        <option value="">— No subject —</option>
                        {subjects.map(sub => <option key={sub.id} value={sub.name}>{sub.name}</option>)}
                      </select>
                      <select value={editState.faculty} onChange={e => setEditState(p => ({ ...p, faculty: e.target.value }))}
                        style={{ fontSize: 11, marginBottom: 4, width: '100%', padding: '4px 6px' }}>
                        <option value="">— No faculty —</option>
                        {faculty.map(f => <option key={f.id} value={f.name}>{f.name}</option>)}
                      </select>
                      <div style={{ display: 'flex', gap: 4 }}>
                        <button onClick={onSaveEdit} className="btn btn-success btn-sm" style={{ fontSize: 10, padding: '2px 8px' }}>
                          <CheckCircle size={10} /> Save
                        </button>
                        <button onClick={onCancelEdit} className="btn btn-ghost btn-sm" style={{ fontSize: 10, padding: '2px 8px' }}>
                          <X size={10} /> Cancel
                        </button>
                      </div>
                    </td>
                  )
                }

                return (
                  <td key={d}
                    onClick={isDraft ? () => onStartEdit(d, s) : undefined}
                    style={{
                      cursor: isDraft ? 'pointer' : 'default',
                      position: 'relative',
                      borderLeft: isSub ? '3px solid var(--amber)' : undefined,
                      background: isSub ? 'rgba(245,158,11,0.06)' : undefined
                    }}>
                    {s.subject ? (
                      <>
                        <div style={{ fontWeight: 600, fontSize: 12 }}>{s.subject}</div>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                          {s.faculty || '—'}
                          {isSub && <span style={{ fontSize: 9, marginLeft: 4, color: 'var(--amber)', fontWeight: 700 }}>SUB</span>}
                        </div>
                        {isSub && s.original_faculty && (
                          <div style={{ fontSize: 10, color: 'var(--text-muted)', fontStyle: 'italic' }}>
                            for {s.original_faculty}
                          </div>
                        )}
                      </>
                    ) : (
                      <span style={{ color: 'var(--text-muted)', fontSize: 12 }}>
                        {isDraft ? 'Click to assign' : 'Free'}
                      </span>
                    )}
                    {isDraft && s.subject && (
                      <Edit3 size={10} style={{ position: 'absolute', top: 4, right: 4, opacity: 0.3 }} />
                    )}
                  </td>
                )
              })}
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}
