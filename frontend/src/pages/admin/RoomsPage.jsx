import { useEffect, useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'
import api from '../../utils/api'
import toast from 'react-hot-toast'

const TYPE_BADGE = { classroom: 'badge-blue', lab: 'badge-teal', hall: 'badge-amber' }

export default function RoomsPage() {
  const [rooms, setRooms] = useState([])
  const [form, setForm] = useState({ room_id: '', type: 'classroom', capacity: 60 })
  const [saving, setSaving] = useState(false)

  const load = () => { api.get('/rooms').then(r => setRooms(r.data)) }
  useEffect(load, [])

  const handleAdd = async () => {
    if (!form.room_id) { toast.error('Room ID required'); return }
    setSaving(true)
    try {
      await api.post('/rooms', form)
      toast.success('Room added!')
      setForm({ room_id: '', type: 'classroom', capacity: 60 })
      load()
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Error')
    } finally { setSaving(false) }
  }

  const toggleAvail = async (room) => {
    await api.patch(`/rooms/${room.id}`, { is_available: room.is_available ? 0 : 1 })
    toast.success('Updated')
    load()
  }

  const del = async (id) => {
    if (!confirm('Delete this room?')) return
    await api.delete(`/rooms/${id}`)
    toast.success('Deleted')
    load()
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <h2>Rooms &amp; Labs</h2>
        <p>Manage available classrooms, labs and halls for scheduling</p>
      </div>
      <div className="grid2" style={{ alignItems: 'start' }}>
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--navy-border)' }}>
            <h3 style={{ fontSize: 15 }}>All Rooms ({rooms.length})</h3>
          </div>
          <table>
            <thead><tr><th>Room ID</th><th>Type</th><th>Capacity</th><th>Status</th><th></th></tr></thead>
            <tbody>
              {rooms.map(r => (
                <tr key={r.id}>
                  <td style={{ fontWeight: 600 }}>{r.room_id}</td>
                  <td><span className={`badge ${TYPE_BADGE[r.type] || 'badge-gray'}`}>{r.type}</span></td>
                  <td>{r.capacity}</td>
                  <td>
                    <button onClick={() => toggleAvail(r)} className={`badge ${r.is_available ? 'badge-green' : 'badge-rose'}`} style={{ cursor: 'pointer', border: 'none', fontSize: 11 }}>
                      {r.is_available ? 'Available' : 'Unavailable'}
                    </button>
                  </td>
                  <td>
                    <button onClick={() => del(r.id)} className="btn btn-ghost btn-xs"><Trash2 size={12} color="var(--rose)" /></button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h3 style={{ fontSize: 15, marginBottom: 18 }}>Add Room / Lab</h3>
          <label>Room ID *</label>
          <input placeholder="e.g. R-106 or Lab-3" value={form.room_id} onChange={e => setForm(p => ({...p, room_id: e.target.value}))} />
          <label>Type</label>
          <select value={form.type} onChange={e => setForm(p => ({...p, type: e.target.value}))}>
            <option value="classroom">Classroom</option>
            <option value="lab">Lab</option>
            <option value="hall">Hall</option>
          </select>
          <label>Capacity</label>
          <input type="number" min="1" value={form.capacity} onChange={e => setForm(p => ({...p, capacity: parseInt(e.target.value)}))} />
          <button className="btn btn-primary" onClick={handleAdd} disabled={saving} style={{ marginTop: 18, width: '100%', justifyContent: 'center' }}>
            {saving ? <span className="spinner" style={{ width: 14, height: 14 }} /> : <><Plus size={14} /> Add Room</>}
          </button>
        </div>
      </div>
    </div>
  )
}
