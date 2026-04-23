import { useEffect, useState } from 'react'
import { Shield, Plus, Trash2, ToggleLeft, ToggleRight, Lock, AlertTriangle } from 'lucide-react'
import api from '../../utils/api'
import toast from 'react-hot-toast'

const CATEGORY_OPTIONS = [
  { value: 'faculty_unavailable_slot', label: 'Faculty unavailable at slot', type: 'hard',
    desc: 'Block a specific faculty member from being scheduled at a particular day and time slot' },
  { value: 'no_consecutive_same_subject', label: 'No consecutive same subject', type: 'soft',
    desc: 'Prevent the same subject from appearing in back-to-back slots for a department' },
  { value: 'max_subject_per_day', label: 'Max subject classes per day', type: 'soft',
    desc: 'Limit how many times a specific subject can appear per day in each department' },
  { value: 'faculty_max_per_day', label: 'Faculty max classes per day', type: 'hard',
    desc: 'Limit how many classes a faculty member can teach per day' },
  { value: 'subject_preferred_slot', label: 'Subject preferred time slots', type: 'soft',
    desc: 'Prefer scheduling a subject during specific time slots' },
]

const MANDATORY = new Set([
  'no_faculty_double_booking', 
  'no_room_double_booking',
  'strict_base_classroom',
  'strict_base_lab',
  'contiguous_lab_blocks',
  'lunch_break_boundary'
])

const IMPLICIT_CONSTRAINTS = [
  { id: 'imp1', name: 'Strict Base Classroom Routing', category: 'strict_base_classroom', type: 'hard', is_builtin: 1, is_enabled: 1 },
  { id: 'imp2', name: 'Strict Base Lab Routing', category: 'strict_base_lab', type: 'hard', is_builtin: 1, is_enabled: 1 },
  { id: 'imp3', name: 'Contiguous Lab Blocks', category: 'contiguous_lab_blocks', type: 'hard', is_builtin: 1, is_enabled: 1 },
  { id: 'imp4', name: 'Lunch Break Boundary Enforcement', category: 'lunch_break_boundary', type: 'hard', is_builtin: 1, is_enabled: 1 },
]

export default function ConstraintsPage() {
  const [constraints, setConstraints] = useState([])
  const [faculty, setFaculty] = useState([])
  const [subjects, setSubjects] = useState([])
  const [tab, setTab] = useState('builtin')

  // Form state
  const [category, setCategory] = useState('')
  const [name, setName] = useState('')
  const [config, setConfig] = useState({})
  const [saving, setSaving] = useState(false)

  const load = () => {
    api.get('/constraints').then(r => setConstraints(r.data)).catch(() => {})
    api.get('/faculty').then(r => setFaculty(r.data)).catch(() => {})
    api.get('/subjects').then(r => setSubjects(r.data)).catch(() => {})
  }
  useEffect(load, [])

  const builtin = [...constraints.filter(c => c.is_builtin === 1), ...IMPLICIT_CONSTRAINTS]
  const custom = constraints.filter(c => c.is_builtin === 0)

  const toggle = async (c) => {
    if (c.is_builtin === 1 && MANDATORY.has(c.category)) {
      toast.error('This constraint is mandatory and cannot be disabled')
      return
    }
    try {
      await api.patch(`/constraints/${c.id}`, { is_enabled: c.is_enabled ? 0 : 1 })
      toast.success(c.is_enabled ? 'Constraint disabled' : 'Constraint enabled')
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    }
  }

  const del = async (id) => {
    if (!confirm('Delete this constraint?')) return
    try {
      await api.delete(`/constraints/${id}`)
      toast.success('Constraint deleted')
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    }
  }

  const catInfo = CATEGORY_OPTIONS.find(c => c.value === category)

  const handleAdd = async () => {
    if (!category || !name) { toast.error('Select a type and enter a name'); return }
    setSaving(true)
    try {
      await api.post('/constraints', {
        name,
        type: catInfo?.type || 'hard',
        category,
        config
      })
      toast.success('Constraint created!')
      setCategory('')
      setName('')
      setConfig({})
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    } finally { setSaving(false) }
  }

  const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

  const renderConfigFields = () => {
    if (!category) return null

    switch (category) {
      case 'faculty_unavailable_slot':
        return (
          <>
            <label>Faculty</label>
            <select value={config.faculty_id || ''} onChange={e => setConfig(p => ({...p, faculty_id: parseInt(e.target.value)}))}>
              <option value="">Select faculty...</option>
              {faculty.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
            </select>
            <div className="grid2">
              <div>
                <label>Day</label>
                <select value={config.day || ''} onChange={e => setConfig(p => ({...p, day: e.target.value}))}>
                  <option value="">Select day...</option>
                  {DAYS.map(d => <option key={d} value={d}>{d}</option>)}
                </select>
              </div>
              <div>
                <label>Slot Index (0-5)</label>
                <input type="number" min={0} max={6} value={config.slot_index ?? ''} placeholder="0"
                  onChange={e => setConfig(p => ({...p, slot_index: parseInt(e.target.value)}))} />
              </div>
            </div>
          </>
        )

      case 'no_consecutive_same_subject':
        return (
          <>
            <label>Subject</label>
            <select value={config.subject_id || ''} onChange={e => setConfig(p => ({...p, subject_id: parseInt(e.target.value)}))}>
              <option value="">Select subject...</option>
              {subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
          </>
        )

      case 'max_subject_per_day':
        return (
          <>
            <label>Subject</label>
            <select value={config.subject_id || ''} onChange={e => setConfig(p => ({...p, subject_id: parseInt(e.target.value)}))}>
              <option value="">Select subject...</option>
              {subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
            <label>Maximum per Day</label>
            <input type="number" min={1} max={6} value={config.max || ''} placeholder="2"
              onChange={e => setConfig(p => ({...p, max: parseInt(e.target.value)}))} />
          </>
        )

      case 'faculty_max_per_day':
        return (
          <>
            <label>Faculty</label>
            <select value={config.faculty_id || ''} onChange={e => setConfig(p => ({...p, faculty_id: parseInt(e.target.value)}))}>
              <option value="">Select faculty...</option>
              {faculty.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
            </select>
            <label>Maximum Classes per Day</label>
            <input type="number" min={1} max={8} value={config.max || ''} placeholder="4"
              onChange={e => setConfig(p => ({...p, max: parseInt(e.target.value)}))} />
          </>
        )

      case 'subject_preferred_slot':
        return (
          <>
            <label>Subject</label>
            <select value={config.subject_id || ''} onChange={e => setConfig(p => ({...p, subject_id: parseInt(e.target.value)}))}>
              <option value="">Select subject...</option>
              {subjects.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
            <label>Preferred Slot Indexes (comma-separated)</label>
            <input value={(config.slots || []).join(',')} placeholder="0,1,2"
              onChange={e => setConfig(p => ({
                ...p,
                slots: e.target.value.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n))
              }))} />
          </>
        )

      default:
        return null
    }
  }

  const describeConstraint = (c) => {
    const cfg = c.config || {}
    const fName = faculty.find(f => f.id === cfg.faculty_id)?.name
    const sName = subjects.find(s => s.id === cfg.subject_id)?.name

    switch (c.category) {
      case 'faculty_unavailable_slot':
        return `${fName || 'Faculty'} cannot teach on ${cfg.day || '?'} at slot ${cfg.slot_index ?? '?'}`
      case 'no_consecutive_same_subject':
        return `${sName || 'Subject'} cannot appear in consecutive slots`
      case 'max_subject_per_day':
        return `${sName || 'Subject'} — max ${cfg.max || '?'} classes per day`
      case 'faculty_max_per_day':
        return `${fName || 'Faculty'} — max ${cfg.max || '?'} classes per day`
      case 'subject_preferred_slot':
        return `${sName || 'Subject'} preferred at slots ${(cfg.slots || []).join(', ')}`
      default:
        return c.category
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Scheduling Constraints</h2>
        <p>Configure built-in rules and add custom constraints for timetable generation</p>
      </div>

      <div className="tabs" style={{ marginBottom: 20 }}>
        <div className={`tab ${tab === 'builtin' ? 'active' : ''}`} onClick={() => setTab('builtin')}>
          Built-in ({builtin.length})
        </div>
        <div className={`tab ${tab === 'custom' ? 'active' : ''}`} onClick={() => setTab('custom')}>
          Custom ({custom.length})
        </div>
      </div>

      {tab === 'builtin' && (
        <div className="card">
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16 }}>
            These core constraints ensure a valid timetable. Mandatory constraints cannot be disabled.
          </div>
          {builtin.map(c => (
            <div key={c.id} style={{
              display: 'flex', alignItems: 'center', gap: 14, padding: '14px 0',
              borderBottom: '1px solid var(--navy-border)'
            }}>
              <button onClick={() => toggle(c)} style={{
                background: 'none', border: 'none', cursor: 'pointer', flexShrink: 0, padding: 0
              }}>
                {MANDATORY.has(c.category) ? (
                  <Lock size={20} color="var(--text-muted)" />
                ) : c.is_enabled ? (
                  <ToggleRight size={22} color="var(--green)" />
                ) : (
                  <ToggleLeft size={22} color="var(--text-muted)" />
                )}
              </button>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontWeight: 600, fontSize: 14, color: c.is_enabled ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                    {c.name}
                  </span>
                  <span className={`badge ${c.type === 'hard' ? 'badge-rose' : 'badge-amber'}`}>{c.type}</span>
                  {MANDATORY.has(c.category) && <span className="badge badge-gray">mandatory</span>}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 3 }}>
                  {c.category === 'no_faculty_double_booking' && 'A faculty member cannot teach two classes at the same time across any departments'}
                  {c.category === 'no_room_double_booking' && 'A room cannot be assigned to two different classes at the same time'}
                  {c.category === 'respect_max_weekly_hours' && 'Faculty will not be scheduled beyond their configured maximum weekly hours'}
                  {c.category === 'balance_workload' && 'Distribute teaching hours evenly among faculty to prevent burnout'}
                  {c.category === 'strict_base_classroom' && 'Theory subjects will strictly be routed to a department\'s designated base classroom'}
                  {c.category === 'strict_base_lab' && 'Lab subjects will strictly be routed to a department\'s designated base lab'}
                  {c.category === 'contiguous_lab_blocks' && 'Lab sessions will be mathematically grouped into 1, 2, or 3 hour continuous blocks on a single day'}
                  {c.category === 'lunch_break_boundary' && 'Lab blocks will be strictly scheduled in morning or afternoon sessions without crossing the lunch break'}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === 'custom' && (
        <div className="grid2" style={{ alignItems: 'start' }}>
          {/* Custom list */}
          <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--navy-border)' }}>
              <h3 style={{ fontSize: 15 }}>Custom Constraints ({custom.length})</h3>
            </div>
            {custom.length === 0 ? (
              <div className="empty-state" style={{ padding: 40 }}>No custom constraints yet. Create one to fine-tune scheduling.</div>
            ) : (
              <div style={{ maxHeight: 480, overflowY: 'auto' }}>
                {custom.map(c => (
                  <div key={c.id} style={{
                    padding: '14px 20px', borderBottom: '1px solid var(--navy-border)',
                    display: 'flex', alignItems: 'flex-start', gap: 12
                  }}>
                    <button onClick={() => toggle(c)} style={{
                      background: 'none', border: 'none', cursor: 'pointer', padding: 0, marginTop: 2
                    }}>
                      {c.is_enabled
                        ? <ToggleRight size={20} color="var(--green)" />
                        : <ToggleLeft size={20} color="var(--text-muted)" />}
                    </button>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 3, color: c.is_enabled ? 'var(--text-primary)' : 'var(--text-muted)' }}>
                        {c.name}
                      </div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{describeConstraint(c)}</div>
                      <span className={`badge ${c.type === 'hard' ? 'badge-rose' : 'badge-amber'}`} style={{ marginTop: 6 }}>{c.type}</span>
                    </div>
                    <button onClick={() => del(c.id)} className="btn btn-ghost btn-xs" style={{ marginTop: 2 }}>
                      <Trash2 size={12} color="var(--rose)" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Add form */}
          <div className="card">
            <h3 style={{ fontSize: 15, marginBottom: 18 }}>Add Custom Constraint</h3>

            <label>Constraint Type</label>
            <select value={category} onChange={e => { setCategory(e.target.value); setConfig({}); }}>
              <option value="">Select type...</option>
              {CATEGORY_OPTIONS.map(o => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>

            {catInfo && (
              <div className="alert alert-info" style={{ marginTop: 10, marginBottom: 4 }}>
                <Shield size={13} style={{ flexShrink: 0, marginTop: 1 }} />
                <span style={{ fontSize: 12 }}>{catInfo.desc}</span>
              </div>
            )}

            <label>Constraint Name</label>
            <input placeholder="e.g. Dr. Sharma unavailable Monday morning"
              value={name} onChange={e => setName(e.target.value)} />

            {renderConfigFields()}

            <button className="btn btn-primary" onClick={handleAdd} disabled={saving || !category}
              style={{ marginTop: 18, width: '100%', justifyContent: 'center' }}>
              {saving
                ? <><span className="spinner" style={{ width: 14, height: 14 }} /> Creating...</>
                : <><Plus size={14} /> Add Constraint</>}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
