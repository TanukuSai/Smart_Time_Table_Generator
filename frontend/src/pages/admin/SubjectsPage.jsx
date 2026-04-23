import { useEffect, useState } from 'react'
import { Plus, Trash2, Edit3, BookOpen, Users, GraduationCap } from 'lucide-react'
import api from '../../utils/api'
import toast from 'react-hot-toast'

export default function SubjectsPage() {
  const [subjects, setSubjects] = useState([])
  const [departments, setGrades] = useState([])
  const [form, setForm] = useState({ name: '', code: '', semester: 1, classes_per_week: 4, department_ids: [], type: 'theory' })
  const [editId, setEditId] = useState(null)
  const [editForm, setEditForm] = useState({})
  const [saving, setSaving] = useState(false)

  const load = () => { 
    api.get('/subjects').then(r => setSubjects(r.data)).catch(() => {}) 
    api.get('/departments').then(r => setGrades(r.data)).catch(() => {})
  }
  useEffect(() => { load() }, [])

  const handleAdd = async () => {
    if (!form.name || !form.code) { toast.error('Name and code are required'); return }
    setSaving(true)
    try {
      await api.post('/subjects', form)
      toast.success('Subject created!')
      setForm({ name: '', code: '', semester: 1, classes_per_week: 4, department_ids: [], type: 'theory' })
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error creating subject')
    } finally { setSaving(false) }
  }

  const startEdit = (s) => {
    setEditId(s.id)
    setEditForm({ name: s.name, code: s.code, semester: s.semester, classes_per_week: s.classes_per_week, type: s.type || 'theory', department_ids: s.departments ? s.departments.map(g => g.id) : [] })
  }

  const saveEdit = async () => {
    try {
      await api.patch(`/subjects/${editId}`, editForm)
      toast.success('Subject updated!')
      setEditId(null)
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error updating')
    }
  }

  const del = async (id, name) => {
    if (!confirm(`Delete subject "${name}"? This will also remove all faculty assignments for this subject.`)) return
    try {
      await api.delete(`/subjects/${id}`)
      toast.success('Subject deleted')
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Subject Management</h2>
        <p>Add subjects, configure weekly class count, and view faculty assignments</p>
      </div>

      <div className="grid2" style={{ alignItems: 'start' }}>
        {/* Subject list */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--navy-border)' }}>
            <h3 style={{ fontSize: 15 }}>All Subjects ({subjects.length})</h3>
          </div>
          <div style={{ maxHeight: 600, overflowY: 'auto' }}>
            {subjects.length === 0 && (
              <div className="empty-state" style={{ padding: 40 }}>No subjects yet. Add one to get started.</div>
            )}
            {subjects.map(s => (
              <div key={s.id} style={{ padding: '14px 20px', borderBottom: '1px solid var(--navy-border)' }}>
                {editId === s.id ? (
                  /* Edit mode */
                  <div>
                    <div className="grid2" style={{ marginBottom: 8 }}>
                      <input value={editForm.name} placeholder="Subject Name"
                        onChange={e => setEditForm(p => ({...p, name: e.target.value}))} style={{ fontSize: 13 }} />
                      <input value={editForm.code} placeholder="Code"
                        onChange={e => setEditForm(p => ({...p, code: e.target.value}))} style={{ fontSize: 13 }} />
                    </div>
                    <div style={{ marginBottom: 8 }}>
                      <select value={editForm.type} onChange={e => setEditForm(p => ({...p, type: e.target.value}))} style={{ fontSize: 13, width: '100%' }}>
                        <option value="theory">Theory</option>
                        <option value="lab">Lab</option>
                      </select>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                      <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Semester:</span>
                      <input type="number" min={1} max={10} value={editForm.semester}
                        onChange={e => setEditForm(p => ({...p, semester: parseInt(e.target.value) || 1}))}
                        style={{ width: 60, fontSize: 13 }} />
                      
                      <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 8 }}>Classes/Week:</span>
                      <input type="number" min={1} max={10} value={editForm.classes_per_week}
                        onChange={e => setEditForm(p => ({...p, classes_per_week: parseInt(e.target.value) || 1}))}
                        style={{ width: 60, fontSize: 13 }} />
                    </div>
                    <div style={{ marginBottom: 12 }}>
                      <span style={{ fontSize: 12, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Assigned Departments:</span>
                      <div className="chip-wrap">
                        {departments.map(g => (
                          <span key={g.id} 
                            onClick={() => {
                              const ids = editForm.department_ids || [];
                              if (ids.includes(g.id)) setEditForm(p => ({...p, department_ids: ids.filter(id => id !== g.id)}));
                              else setEditForm(p => ({...p, department_ids: [...ids, g.id]}));
                            }}
                            className={`chip ${editForm.department_ids?.includes(g.id) ? 'chip-blue' : ''}`}
                            style={{ cursor: 'pointer', fontSize: 11, opacity: editForm.department_ids?.includes(g.id) ? 1 : 0.6 }}>
                            {g.name}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button className="btn btn-primary btn-xs" onClick={saveEdit}>Save</button>
                      <button className="btn btn-ghost btn-xs" onClick={() => setEditId(null)}>Cancel</button>
                    </div>
                  </div>
                ) : (
                  /* Display mode */
                  <>
                    <div className="flex-between" style={{ marginBottom: 8 }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <div style={{
                            width: 30, height: 30, borderRadius: 8,
                            background: s.type === 'lab' ? 'rgba(244,63,94,0.12)' : 'rgba(245,158,11,0.12)', 
                            border: `1px solid ${s.type === 'lab' ? 'rgba(244,63,94,0.25)' : 'rgba(245,158,11,0.25)'}`,
                            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0
                          }}>
                            <BookOpen size={14} color={s.type === 'lab' ? 'var(--rose)' : 'var(--amber)'} />
                          </div>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                              <span style={{ fontWeight: 600, fontSize: 14 }}>{s.name}</span>
                              <span className={`badge ${s.type === 'lab' ? 'badge-rose' : 'badge-blue'}`} style={{ padding: '2px 6px', fontSize: 10 }}>
                                {s.type === 'lab' ? 'Lab' : 'Theory'}
                              </span>
                            </div>
                            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Code: {s.code}</div>
                          </div>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button onClick={() => startEdit(s)} className="btn btn-ghost btn-xs"><Edit3 size={12} /></button>
                        <button onClick={() => del(s.id, s.name)} className="btn btn-ghost btn-xs"><Trash2 size={12} color="var(--rose)" /></button>
                      </div>
                    </div>

                    {/* Stats row */}
                    <div style={{ display: 'flex', gap: 16, marginBottom: 8 }}>
                      <div style={{
                        display: 'flex', alignItems: 'center', gap: 6, fontSize: 12,
                        background: 'rgba(59,130,246,0.08)', border: '1px solid rgba(59,130,246,0.2)',
                        borderRadius: 8, padding: '4px 10px'
                      }}>
                        <span style={{ fontWeight: 700, color: 'var(--blue)', fontFamily: 'var(--font-display)' }}>
                          Sem {s.semester}
                        </span>
                      </div>
                      <div style={{
                        display: 'flex', alignItems: 'center', gap: 6, fontSize: 12,
                        background: 'rgba(20,184,166,0.08)', border: '1px solid rgba(20,184,166,0.2)',
                        borderRadius: 8, padding: '4px 10px'
                      }}>
                        <span style={{ fontWeight: 700, color: 'var(--teal)', fontFamily: 'var(--font-display)' }}>
                          {s.classes_per_week}
                        </span>
                        <span style={{ color: 'var(--text-muted)' }}>classes/week</span>
                      </div>
                      <div style={{
                        display: 'flex', alignItems: 'center', gap: 6, fontSize: 12,
                        background: 'rgba(245,158,11,0.08)', border: '1px solid rgba(245,158,11,0.2)',
                        borderRadius: 8, padding: '4px 10px'
                      }}>
                        <Users size={12} color="var(--amber)" />
                        <span style={{ color: 'var(--text-muted)' }}>{s.faculty_count} faculty</span>
                      </div>
                    </div>

                    {/* Faculty chips */}
                    {s.faculty?.length > 0 && (
                      <div style={{ marginBottom: 6 }}>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Taught by:</div>
                        <div className="chip-wrap">
                          {s.faculty.map(f => (
                            <span key={f.id} className="chip" style={{ fontSize: 11 }}>{f.name}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Department chips */}
                    {s.departments?.length > 0 && (
                      <div>
                        <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 4 }}>Departments:</div>
                        <div className="chip-wrap">
                          {s.departments.map(g => (
                            <span key={g.id} className="chip chip-blue" style={{ fontSize: 11 }}>{g.name}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Add form */}
        <div className="card">
          <h3 style={{ fontSize: 15, marginBottom: 18 }}>Add New Subject</h3>

          <label>Subject Name *</label>
          <input placeholder="e.g. Mathematics" value={form.name}
            onChange={e => setForm(p => ({...p, name: e.target.value}))} />

          <div className="grid2">
            <div>
              <label>Subject Code *</label>
              <input placeholder="e.g. MATH" value={form.code}
                onChange={e => setForm(p => ({...p, code: e.target.value.toUpperCase()}))} />
            </div>
            <div>
              <label>Type *</label>
              <select value={form.type} onChange={e => setForm(p => ({...p, type: e.target.value}))}>
                <option value="theory">Theory</option>
                <option value="lab">Lab</option>
              </select>
            </div>
          </div>

          <label>Semester</label>
          <input type="number" min={1} max={10} value={form.semester}
            onChange={e => setForm(p => ({...p, semester: parseInt(e.target.value) || 1}))} />

          <label>Classes Per Week</label>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 4 }}>
            <input type="range" min={1} max={10} value={form.classes_per_week}
              onChange={e => setForm(p => ({...p, classes_per_week: parseInt(e.target.value)}))}
              style={{ flex: 1, height: 4, cursor: 'pointer' }} />
            <div style={{
              width: 44, height: 44, borderRadius: 12,
              background: 'rgba(20,184,166,0.12)', border: '1px solid rgba(20,184,166,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 18, color: 'var(--teal)'
            }}>
              {form.classes_per_week}
            </div>
          </div>

          <label style={{ marginTop: 16, display: 'block' }}>Assign Departments</label>
          <div className="chip-wrap" style={{ marginTop: 8, marginBottom: 16 }}>
            {departments.map(g => (
              <span key={g.id} 
                onClick={() => {
                  const ids = form.department_ids || [];
                  if (ids.includes(g.id)) setForm(p => ({...p, department_ids: ids.filter(id => id !== g.id)}));
                  else setForm(p => ({...p, department_ids: [...ids, g.id]}));
                }}
                className={`chip ${form.department_ids?.includes(g.id) ? 'chip-blue' : ''}`}
                style={{ cursor: 'pointer', fontSize: 12, opacity: form.department_ids?.includes(g.id) ? 1 : 0.6 }}>
                {g.name}
              </span>
            ))}
          </div>

          <div className="alert alert-info" style={{ marginTop: 16 }}>
            <BookOpen size={14} style={{ flexShrink: 0, marginTop: 1 }} />
            <span style={{ fontSize: 12.5 }}>
              Classes per week determines how many times this subject appears in a department's weekly timetable
              during generation. You can assign faculty to this subject from the Faculty page.
            </span>
          </div>

          <button className="btn btn-primary" onClick={handleAdd} disabled={saving}
            style={{ marginTop: 18, width: '100%', justifyContent: 'center' }}>
            {saving
              ? <><span className="spinner" style={{ width: 14, height: 14 }} /> Creating...</>
              : <><Plus size={14} /> Add Subject</>}
          </button>
        </div>
      </div>
    </div>
  )
}
