import { useEffect, useState } from 'react'
import { Plus, Trash2, GraduationCap, User, Edit3 } from 'lucide-react'
import api from '../../utils/api'
import toast from 'react-hot-toast'

export default function DepartmentsPage() {
  const [departments, setDepartments] = useState([])
  const [rooms, setRooms] = useState([])
  const [form, setForm] = useState({ name: '', level: 'UG', semester: 1, section: '', strength: 40, room_id: '', lab_id: '' })
  const [saving, setSaving] = useState(false)
  const [editId, setEditId] = useState(null)
  const [editRoom, setEditRoom] = useState('')
  const [editLab, setEditLab] = useState('')

  const load = () => { 
    api.get('/departments').then(r => setDepartments(r.data)).catch(() => {}) 
    api.get('/rooms').then(r => setRooms(r.data)).catch(() => {})
  }
  useEffect(load, [])

  const handleAdd = async () => {
    if (!form.name || !form.section) { toast.error('Name and section are required'); return }
    setSaving(true)
    try {
      const payload = { ...form }
      if (payload.room_id === '') payload.room_id = null;
      else payload.room_id = parseInt(payload.room_id);
      if (payload.lab_id === '') payload.lab_id = null;
      else payload.lab_id = parseInt(payload.lab_id);

      await api.post('/departments', payload)
      toast.success('Department added!')
      setForm({ name: '', level: 'UG', semester: 1, section: '', strength: 40, room_id: '', lab_id: '' })
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error creating department')
    } finally { setSaving(false) }
  }

  const startEdit = (g) => {
    setEditId(g.id)
    setEditRoom(g.room_id || '')
    setEditLab(g.lab_id || '')
  }

  const saveEdit = async (g) => {
    try {
      await api.patch(`/departments/${g.id}`, { 
        room_id: editRoom === '' ? null : parseInt(editRoom),
        lab_id: editLab === '' ? null : parseInt(editLab)
      })
      toast.success('Department updated!')
      setEditId(null)
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error updating')
    }
  }

  const del = async (id, name) => {
    if (!confirm(`Delete department "${name}"? This will also delete its timetable, faculty assignments, and student account.`)) return
    try {
      await api.delete(`/departments/${id}`)
      toast.success('Department deleted')
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    }
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Department Management</h2>
        <p>Add and manage class departments — each department gets its own timetable and student account</p>
      </div>

      <div className="grid2" style={{ alignItems: 'start' }}>
        {/* Department list */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--navy-border)' }}>
            <h3 style={{ fontSize: 15 }}>All Departments ({departments.length})</h3>
          </div>
          {departments.length === 0 ? (
            <div className="empty-state" style={{ padding: 40 }}>No departments yet. Add one to get started.</div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table>
                <thead>
                  <tr>
                    <th>Department</th>
                    <th>Level</th>
                    <th>Semester</th>
                    <th>Section</th>
                    <th>Strength</th>
                    <th>Base Classroom</th>
                    <th>Base Lab</th>
                    <th>Student Login</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {departments.map(g => (
                    <tr key={g.id}>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <div style={{
                            width: 32, height: 32, borderRadius: 8,
                            background: 'rgba(96,165,250,0.12)', border: '1px solid rgba(96,165,250,0.25)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center'
                          }}>
                            <GraduationCap size={15} color="#93c5fd" />
                          </div>
                          <span style={{ fontWeight: 700, fontFamily: 'var(--font-display)', fontSize: 15 }}>{g.name}</span>
                        </div>
                      </td>
                      <td>
                        <span className="badge badge-purple">{g.level}</span>
                      </td>
                      <td>
                        <span className="badge badge-amber">Sem {g.semester}</span>
                      </td>
                      <td>
                        <span className="badge badge-blue">{g.section}</span>
                      </td>
                      <td>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                          <span style={{ fontWeight: 600, fontSize: 14, fontFamily: 'var(--font-display)' }}>{g.strength}</span>
                          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>students</span>
                        </div>
                      </td>
                      <td>
                        {editId === g.id ? (
                          <div className="flex gap-2">
                            <select value={editRoom} onChange={e => setEditRoom(e.target.value)} style={{ padding: '2px 6px', fontSize: 12 }}>
                              <option value="">None</option>
                              {rooms.filter(r => r.type === 'classroom').map(r => (
                                <option key={r.id} value={r.id}>{r.room_id}</option>
                              ))}
                            </select>
                            <button className="btn btn-primary btn-xs" onClick={() => saveEdit(g)}>Save</button>
                            <button className="btn btn-ghost btn-xs" onClick={() => setEditId(null)}>Cancel</button>
                          </div>
                        ) : (
                          <div className="flex gap-2" style={{ alignItems: 'center' }}>
                            {g.room_name ? (
                              <span className="badge badge-amber">Room {g.room_name}</span>
                            ) : (
                              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>No Base Classroom</span>
                            )}
                            <button onClick={() => startEdit(g)} className="btn btn-ghost btn-xs" title="Edit Classroom" style={{ padding: 2 }}>
                              <Edit3 size={11} />
                            </button>
                          </div>
                        )}
                      </td>
                      <td>
                        {editId === g.id ? (
                          <div className="flex gap-2">
                            <select value={editLab} onChange={e => setEditLab(e.target.value)} style={{ padding: '2px 6px', fontSize: 12 }}>
                              <option value="">None</option>
                              {rooms.filter(r => r.type === 'lab').map(r => (
                                <option key={r.id} value={r.id}>{r.room_id}</option>
                              ))}
                            </select>
                          </div>
                        ) : (
                          <div className="flex gap-2" style={{ alignItems: 'center' }}>
                            {g.lab_name ? (
                              <span className="badge badge-rose">Lab {g.lab_name}</span>
                            ) : (
                              <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>No Base Lab</span>
                            )}
                          </div>
                        )}
                      </td>
                      <td>
                        {g.student_account ? (
                          <div style={{ fontSize: 11 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 4, color: 'var(--teal)' }}>
                              <User size={11} />
                              <span style={{ fontWeight: 600 }}>{g.student_account.email}</span>
                            </div>
                            <div style={{ color: 'var(--text-muted)', marginTop: 1 }}>Pass: student123</div>
                          </div>
                        ) : (
                          <span style={{ fontSize: 11, color: 'var(--text-muted)' }}>—</span>
                        )}
                      </td>
                      <td>
                        <button onClick={() => del(g.id, g.name)} className="btn btn-ghost btn-xs">
                          <Trash2 size={12} color="var(--rose)" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Add form */}
        <div className="card">
          <h3 style={{ fontSize: 15, marginBottom: 18 }}>Add New Department</h3>

          <label>Department Name *</label>
          <input placeholder="e.g. BTech-CSE-A" value={form.name}
            onChange={e => setForm(p => ({...p, name: e.target.value}))} />

          <label>Department Level *</label>
          <input type="text" placeholder="e.g. UG, PG" value={form.level}
            onChange={e => setForm(p => ({...p, level: e.target.value}))} />

          <label>Semester *</label>
          <input type="number" min={1} max={10} value={form.semester}
            onChange={e => setForm(p => ({...p, semester: parseInt(e.target.value) || 1}))} />

          <label>Section *</label>
          <input placeholder="e.g. A, B, C" value={form.section}
            onChange={e => setForm(p => ({...p, section: e.target.value}))} />

          <label>Student Strength</label>
          <input type="number" min={1} max={200} value={form.strength}
            onChange={e => setForm(p => ({...p, strength: parseInt(e.target.value) || 1}))} />

          <div className="grid2">
            <div>
              <label>Base Classroom (Theory)</label>
              <select value={form.room_id} onChange={e => setForm(p => ({...p, room_id: e.target.value}))}>
                <option value="">Select a classroom...</option>
                {rooms.filter(r => r.type === 'classroom').map(r => (
                  <option key={r.id} value={r.id}>{r.room_id}</option>
                ))}
              </select>
            </div>
            <div>
              <label>Base Lab</label>
              <select value={form.lab_id} onChange={e => setForm(p => ({...p, lab_id: e.target.value}))}>
                <option value="">Select a lab...</option>
                {rooms.filter(r => r.type === 'lab').map(r => (
                  <option key={r.id} value={r.id}>{r.room_id}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="alert alert-info" style={{ marginTop: 16 }}>
            <GraduationCap size={14} style={{ flexShrink: 0, marginTop: 1 }} />
            <span style={{ fontSize: 12.5 }}>
              A student login account is <strong>automatically created</strong> for each department.
              Students can log in to view only their class timetable. Default password: <code>student123</code>
            </span>
          </div>

          <button className="btn btn-primary" onClick={handleAdd} disabled={saving}
            style={{ marginTop: 18, width: '100%', justifyContent: 'center' }}>
            {saving
              ? <><span className="spinner" style={{ width: 14, height: 14 }} /> Adding...</>
              : <><Plus size={14} /> Add Department</>}
          </button>
        </div>
      </div>
    </div>
  )
}
