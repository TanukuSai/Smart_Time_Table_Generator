import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import Layout from './components/Layout'
import Dashboard from './pages/admin/Dashboard'
import FacultyPage from './pages/admin/FacultyPage'
import RoomsPage from './pages/admin/RoomsPage'
import LeavesPage from './pages/admin/LeavesPage'
import GeneratePage from './pages/admin/GeneratePage'
import SubjectsPage from './pages/admin/SubjectsPage'
import ConstraintsPage from './pages/admin/ConstraintsPage'
import DepartmentsPage from './pages/admin/DepartmentsPage'
import HistoryPage from './pages/admin/HistoryPage'
import TimetablePage from './pages/shared/TimetablePage'
import FacDashboard from './pages/faculty/FacDashboard'
import FacSchedule from './pages/faculty/FacSchedule'
import FacLeave from './pages/faculty/FacLeave'
import StuTimetable from './pages/student/StuTimetable'
import StuFacultyToday from './pages/student/StuFacultyToday'

function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth()
  if (loading) return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}><div className="spinner" /></div>
  if (!user) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/" replace />
  return children
}

function RoleRedirect() {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  if (user.role === 'admin') return <Navigate to="/admin/dashboard" replace />
  if (user.role === 'faculty') return <Navigate to="/faculty/dashboard" replace />
  return <Navigate to="/student/timetable" replace />
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: '#1a2435',
              color: '#f0f4ff',
              border: '1px solid #2e3d55',
              fontFamily: 'DM Sans, sans-serif',
              fontSize: '14px',
            },
            success: { iconTheme: { primary: '#10b981', secondary: '#1a2435' } },
            error: { iconTheme: { primary: '#f43f5e', secondary: '#1a2435' } },
          }}
        />
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<RoleRedirect />} />

          {/* Admin routes */}
          <Route path="/admin" element={<ProtectedRoute allowedRoles={['admin']}><Layout /></ProtectedRoute>}>
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="timetable" element={<TimetablePage />} />
            <Route path="subjects" element={<SubjectsPage />} />
            <Route path="faculty" element={<FacultyPage />} />
            <Route path="departments" element={<DepartmentsPage />} />
            <Route path="rooms" element={<RoomsPage />} />
            <Route path="constraints" element={<ConstraintsPage />} />
            <Route path="leaves" element={<LeavesPage />} />
            <Route path="generate" element={<GeneratePage />} />
            <Route path="history" element={<HistoryPage />} />
          </Route>

          {/* Faculty routes */}
          <Route path="/faculty" element={<ProtectedRoute allowedRoles={['faculty']}><Layout /></ProtectedRoute>}>
            <Route path="dashboard" element={<FacDashboard />} />
            <Route path="schedule" element={<FacSchedule />} />
            <Route path="leave" element={<FacLeave />} />
          </Route>

          {/* Student routes */}
          <Route path="/student" element={<ProtectedRoute allowedRoles={['student']}><Layout /></ProtectedRoute>}>
            <Route path="timetable" element={<StuTimetable />} />
            <Route path="faculty-today" element={<StuFacultyToday />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
