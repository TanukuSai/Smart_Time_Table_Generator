const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
const DAY_FULL = { Mon: 'Monday', Tue: 'Tuesday', Wed: 'Wednesday', Thu: 'Thursday', Fri: 'Friday' }

export default function TimetableGrid({ data, highlightFaculty }) {
  if (!data || !Object.keys(data).length) {
    return <div className="empty-state">No timetable data available.</div>
  }

  const allSlots = Object.values(data)[0] || []
  const numSlots = allSlots.length

  return (
    <div style={{ overflowX: 'auto' }}>
      <div className="tt-grid" style={{ gridTemplateColumns: `90px repeat(${DAYS.length}, 1fr)`, minWidth: 600 }}>
        {/* Header row */}
        <div className="tt-cell tt-head" style={{ display: 'flex', alignItems: 'center' }}>Slot</div>
        {DAYS.map(d => (
          <div key={d} className="tt-cell tt-head" style={{ textAlign: 'center' }}>{DAY_FULL[d]}</div>
        ))}

        {/* Slot rows */}
        {Array.from({ length: numSlots }).map((_, i) => {
          const sample = Object.values(data).flatMap(d => d).find(s => s.slot_index === i)
          const time = sample?.slot_time || ''
          const isBreak = Object.values(data).every(d => (d[i]?.is_break))
          return (
            <div key={i} style={{ display: 'contents' }}>
              <div className="tt-cell tt-head" style={{ fontSize: 10.5, color: 'var(--text-muted)' }}>{time}</div>
              {DAYS.map(day => {
                const slot = data[day]?.[i]
                if (!slot) return <div key={day} className="tt-cell" />
                if (slot.is_break) return <div key={day} className="tt-cell tt-break">Break</div>
                const isHL = highlightFaculty && slot.faculty_name === highlightFaculty
                const isSub = slot.is_substituted
                return (
                  <div key={day} className={`tt-cell ${isHL ? 'tt-slot-fac-class' : 'tt-slot'}`}
                    style={isSub ? {
                      borderLeft: '3px solid var(--amber)',
                      background: 'rgba(245,158,11,0.06)'
                    } : {}}>
                    {slot.subject_name && <div className="tt-slot-sub">{slot.subject_name}</div>}
                    {slot.faculty_name && (
                      <div className="tt-slot-fac" style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                        {slot.faculty_name}
                        {isSub && (
                          <span style={{
                            fontSize: 9, padding: '1px 5px', borderRadius: 4,
                            background: 'rgba(245,158,11,0.2)', color: 'var(--amber)',
                            fontWeight: 700, letterSpacing: '0.03em'
                          }}>SUB</span>
                        )}
                      </div>
                    )}
                    {isSub && slot.original_faculty_name && (
                      <div style={{ fontSize: 10, color: 'var(--text-muted)', fontStyle: 'italic', marginTop: 1 }}>
                        covering for {slot.original_faculty_name}
                      </div>
                    )}
                    {slot.room_name && <div className="tt-slot-room">{slot.room_name}</div>}
                  </div>
                )
              })}
            </div>
          )
        })}
      </div>
    </div>
  )
}
