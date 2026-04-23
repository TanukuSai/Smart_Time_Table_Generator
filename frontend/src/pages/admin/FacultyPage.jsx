import { useEffect, useState } from 'react'
import { Plus, Trash2, ToggleLeft, ToggleRight, Edit3, AlertTriangle } from 'lucide-react'
import api from '../../utils/api'
import toast from 'react-hot-toast'

export default function FacultyPage() {
  const [faculty, setFaculty] = useState([])
  const [subjects, setSubjects] = useState([])
  const [departments, setGrades] = useState([])
  const [form, setForm] = useState({
    name: '', email: '', password: 'faculty123', employee_code: '',
    max_weekly_hours: 20, subject_ids: [], grade_subject_pairs: []
  })
  const [selSubjects, setSelSubjects] = useState([])
  const [gsPairs, setGsPairs] = useState([]) // [{department_id, subject_id}]
  const [newGrade, setNewGrade] = useState('')
  const [newSubject, setNewSubject] = useState('')
  const [saving, setSaving] = useState(false)

  // Edit states
  const [editId, setEditId] = useState(null)
  const [editMaxHours, setEditMaxHours] = useState(20)
  const [editSelSubjects, setEditSelSubjects] = useState([])
  const [editGsPairs, setEditGsPairs] = useState([])
  const [editNewGrade, setEditNewGrade] = useState('')
  const [editNewSubject, setEditNewSubject] = useState('')

  const load = () => {
    api.get('/faculty').then(r => setFaculty(r.data))
    api.get('/subjects').then(r => setSubjects(r.data))
    api.get('/departments').then(r => setGrades(r.data))
  }
  useEffect(load, [])

  const togglePresent = async (fac) => {
    await api.patch(`/faculty/${fac.id}`, { is_present: fac.is_present ? 0 : 1 })
    toast.success('Attendance updated')
    load()
  }

  const triggerEmergencyLeave = async (fac) => {
    if (!confirm(`Trigger Emergency Sick Leave for ${fac.name} today? This will automatically generate substitutions for their classes.`)) return
    try {
      await api.post('/leaves/emergency', { faculty_id: fac.id })
      toast.success(`Emergency leave triggered for ${fac.name}`)
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Failed to trigger emergency leave')
    }
  }

  const deleteFaculty = async (id, name) => {
    if (!confirm(`Remove ${name}?`)) return
    await api.delete(`/faculty/${id}`)
    toast.success('Faculty removed')
    load()
  }

  const addGsPair = () => {
    if (!newGrade || !newSubject) return
    const already = gsPairs.find(p => p.department_id == newGrade && p.subject_id == newSubject)
    if (already) return
    const department = departments.find(g => g.id == newGrade)
    const subject = subjects.find(s => s.id == newSubject)
    setGsPairs(prev => [...prev, { department_id: parseInt(newGrade), subject_id: parseInt(newSubject), grade_name: department?.name, subject_name: subject?.name }])
  }

  const removeGsPair = (i) => setGsPairs(prev => prev.filter((_, idx) => idx !== i))

  const toggleSubject = (sid) => {
    setSelSubjects(prev => prev.includes(sid) ? prev.filter(x => x !== sid) : [...prev, sid])
  }

  const startEdit = (f) => {
    setEditId(f.id)
    setEditMaxHours(f.max_weekly_hours || 20)
    setEditSelSubjects(f.subjects ? f.subjects.map(s => s.id) : [])
    setEditGsPairs(f.grade_subjects ? f.grade_subjects.map(gs => ({
      department_id: gs.department_id,
      subject_id: gs.subject_id,
      grade_name: gs.grade_name,
      subject_name: gs.subject_name
    })) : [])
    setEditNewGrade('')
    setEditNewSubject('')
  }

  const saveEdit = async () => {
    try {
      await api.patch(`/faculty/${editId}`, {
        max_weekly_hours: editMaxHours,
        subject_ids: editSelSubjects,
        grade_subject_pairs: editGsPairs.map(p => ({ department_id: p.department_id, subject_id: p.subject_id }))
      })
      toast.success('Faculty updated!')
      setEditId(null)
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error updating faculty')
    }
  }

  const addEditGsPair = () => {
    if (!editNewGrade || !editNewSubject) return
    const already = editGsPairs.find(p => p.department_id == editNewGrade && p.subject_id == editNewSubject)
    if (already) return
    const department = departments.find(g => g.id == editNewGrade)
    const subject = subjects.find(s => s.id == editNewSubject)
    setEditGsPairs(prev => [...prev, { department_id: parseInt(editNewGrade), subject_id: parseInt(editNewSubject), grade_name: department?.name, subject_name: subject?.name }])
  }

  const removeEditGsPair = (i) => setEditGsPairs(prev => prev.filter((_, idx) => idx !== i))

  const toggleEditSubject = (sid) => {
    setEditSelSubjects(prev => prev.includes(sid) ? prev.filter(x => x !== sid) : [...prev, sid])
  }

  const handleSave = async () => {
    if (!form.name || !form.email || !form.employee_code) { toast.error('Fill required fields'); return }
    setSaving(true)
    try {
      await api.post('/faculty', {
        ...form,
        subject_ids: selSubjects,
        grade_subject_pairs: gsPairs.map(p => ({ department_id: p.department_id, subject_id: p.subject_id }))
      })
      toast.success('Faculty added!')
      setForm({ name: '', email: '', password: 'faculty123', employee_code: '', max_weekly_hours: 20, subject_ids: [], grade_subject_pairs: [] })
      setSelSubjects([])
      setGsPairs([])
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error saving faculty')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Faculty Management</h2>
        <p>Add and manage faculty — one teacher can teach multiple subjects across multiple departments</p>
      </div>

      <div className="grid2" style={{ alignItems: 'start' }}>
        {/* List */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--navy-border)' }}>
            <h3 style={{ fontSize: 15 }}>All Faculty ({faculty.length})</h3>
          </div>
          <div style={{ maxHeight: 580, overflowY: 'auto' }}>
            {faculty.map(f => (
              <div key={f.id} style={{ padding: '14px 20px', borderBottom: '1px solid var(--navy-border)' }}>
                {editId === f.id ? (
                  <div>
                    <div className="flex-between" style={{ marginBottom: 12 }}>
                      <div className="flex gap-2">
                        <div className="avatar" style={{ fontSize: 11 }}>{f.name?.split(' ').map(n=>n[0]).slice(0,2).join('')}</div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 13 }}>{f.name}</div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{f.email} · {f.employee_code}</div>
                        </div>
                      </div>
                    </div>
                    
                    <div style={{ marginBottom: 12 }}>
                      <label style={{ fontSize: 12, marginBottom: 4, display: 'block' }}>Max Weekly Hours</label>
                      <input type="number" min="1" max="40" value={editMaxHours} onChange={e => setEditMaxHours(parseInt(e.target.value) || 20)} style={{ padding: '4px 8px', fontSize: 13, width: 100 }} />
                    </div>

                    <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 6 }}>Subjects taught</div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 12 }}>
                      {subjects.map(s => (
                        <button key={s.id} onClick={() => toggleEditSubject(s.id)}
                          className="btn btn-xs"
                          style={{
                            background: editSelSubjects.includes(s.id) ? 'rgba(245,158,11,0.2)' : 'transparent',
                            color: editSelSubjects.includes(s.id) ? 'var(--amber)' : 'var(--text-muted)',
                            border: `1px solid ${editSelSubjects.includes(s.id) ? 'rgba(245,158,11,0.4)' : 'var(--navy-border)'}`,
                          }}>
                          {s.name}
                        </button>
                      ))}
                    </div>

                    <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 6 }}>Department → Subject Assignments</div>
                    <div className="flex gap-2" style={{ marginBottom: 8 }}>
                      <select value={editNewGrade} onChange={e => setEditNewGrade(e.target.value)} style={{ flex: 1, padding: '4px 8px', fontSize: 12 }}>
                        <option value="">Select department...</option>
                        {departments.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
                      </select>
                      <select value={editNewSubject} onChange={e => setEditNewSubject(e.target.value)} style={{ flex: 1, padding: '4px 8px', fontSize: 12 }}>
                        <option value="">Select subject...</option>
                        {subjects.filter(s => editSelSubjects.includes(s.id)).map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                      </select>
                      <button className="btn btn-ghost btn-sm" onClick={addEditGsPair}><Plus size={13} /></button>
                    </div>
                    <div className="chip-wrap" style={{ marginBottom: 12 }}>
                      {editGsPairs.map((p, i) => (
                        <span key={i} className="chip chip-teal" style={{ fontSize: 11 }}>
                          {p.grade_name} · {p.subject_name}
                          <span className="chip-rm" onClick={() => removeEditGsPair(i)}>×</span>
                        </span>
                      ))}
                    </div>

                    <div className="flex gap-2">
                      <button className="btn btn-primary btn-xs" onClick={saveEdit}>Save Changes</button>
                      <button className="btn btn-ghost btn-xs" onClick={() => setEditId(null)}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="flex-between" style={{ marginBottom: 8 }}>
                      <div className="flex gap-2">
                        <div className="avatar" style={{ fontSize: 11 }}>{f.name?.split(' ').map(n=>n[0]).slice(0,2).join('')}</div>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 13 }}>{f.name}</div>
                          <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>{f.email} · {f.employee_code}</div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button onClick={() => triggerEmergencyLeave(f)} className="btn btn-ghost btn-xs" title="Emergency Leave" style={{ color: 'var(--amber)' }}>
                          <AlertTriangle size={12} />
                        </button>
                        <button onClick={() => startEdit(f)} className="btn btn-ghost btn-xs" title="Edit faculty">
                          <Edit3 size={12} />
                        </button>
                        <button onClick={() => togglePresent(f)} className="btn btn-ghost btn-xs" title="Toggle attendance">
                          {f.is_present ? <ToggleRight size={14} color="var(--green)" /> : <ToggleLeft size={14} color="var(--rose)" />}
                          {f.is_present ? 'Present' : 'Absent'}
                        </button>
                        <button onClick={() => deleteFaculty(f.id, f.name)} className="btn btn-ghost btn-xs">
                          <Trash2 size={12} color="var(--rose)" />
                        </button>
                      </div>
                    </div>
                    <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginBottom: 4 }}>Subjects taught:</div>
                    <div className="chip-wrap" style={{ marginBottom: 6 }}>
                      {f.subjects?.map(s => <span key={s.id} className="chip" style={{ fontSize: 11 }}>{s.name}</span>)}
                    </div>
                    <div style={{ fontSize: 11.5, color: 'var(--text-muted)', marginBottom: 4 }}>Department assignments:</div>
                    <div className="chip-wrap">
                      {f.grade_subjects?.map((gs, i) => (
                        <span key={i} className="chip chip-blue" style={{ fontSize: 11 }}>{gs.grade_name} · {gs.subject_name}</span>
                      ))}
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Add form */}
        <div className="card">
          <h3 style={{ fontSize: 15, marginBottom: 18 }}>Add New Faculty</h3>

          <div className="grid2">
            <div>
              <label>Full Name *</label>
              <input placeholder="Dr. A. Kumar" value={form.name} onChange={e => setForm(p => ({...p, name: e.target.value}))} />
            </div>
            <div>
              <label>Employee Code *</label>
              <input placeholder="EMP006" value={form.employee_code} onChange={e => setForm(p => ({...p, employee_code: e.target.value}))} />
            </div>
          </div>

          <label>Email *</label>
          <input type="email" placeholder="faculty@tkrec.edu" value={form.email} onChange={e => setForm(p => ({...p, email: e.target.value}))} />

          <div className="grid2">
            <div>
              <label>Login Password</label>
              <input value={form.password} onChange={e => setForm(p => ({...p, password: e.target.value}))} />
            </div>
            <div>
              <label>Max Weekly Hours</label>
              <input type="number" min="1" max="40" value={form.max_weekly_hours} onChange={e => setForm(p => ({...p, max_weekly_hours: parseInt(e.target.value)}))} />
            </div>
          </div>

          <div className="sep" />

          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, color: 'var(--text-secondary)' }}>Subjects this faculty teaches</div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {subjects.map(s => (
              <button key={s.id} onClick={() => toggleSubject(s.id)}
                className="btn btn-xs"
                style={{
                  background: selSubjects.includes(s.id) ? 'rgba(245,158,11,0.2)' : 'transparent',
                  color: selSubjects.includes(s.id) ? 'var(--amber)' : 'var(--text-muted)',
                  border: `1px solid ${selSubjects.includes(s.id) ? 'rgba(245,158,11,0.4)' : 'var(--navy-border)'}`,
                }}>
                {s.name}
              </button>
            ))}
          </div>

          <div className="sep" />

          <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 10, color: 'var(--text-secondary)' }}>
            Department → Subject Assignments
            <span style={{ fontWeight: 400, fontSize: 12, color: 'var(--text-muted)', marginLeft: 8 }}>
              (one teacher can teach different subjects to different departments)
            </span>
          </div>
          <div className="flex gap-2" style={{ marginBottom: 8 }}>
            <select value={newGrade} onChange={e => setNewGrade(e.target.value)} style={{ flex: 1 }}>
              <option value="">Select department...</option>
              {departments.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
            </select>
            <select value={newSubject} onChange={e => setNewSubject(e.target.value)} style={{ flex: 1 }}>
              <option value="">Select subject...</option>
              {subjects.filter(s => selSubjects.includes(s.id)).map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
            </select>
            <button className="btn btn-ghost btn-sm" onClick={addGsPair}><Plus size={13} /></button>
          </div>
          <div className="chip-wrap">
            {gsPairs.map((p, i) => (
              <span key={i} className="chip chip-teal" style={{ fontSize: 11 }}>
                {p.grade_name} · {p.subject_name}
                <span className="chip-rm" onClick={() => removeGsPair(i)}>×</span>
              </span>
            ))}
          </div>

          <button className="btn btn-primary" onClick={handleSave} disabled={saving} style={{ marginTop: 18, width: '100%', justifyContent: 'center' }}>
            {saving ? <><span className="spinner" style={{ width: 14, height: 14 }} /> Saving...</> : <><Plus size={14} /> Add Faculty</>}
          </button>
        </div>
      </div>
    </div>
  )
}
