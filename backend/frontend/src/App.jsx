import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import VerifyEmailPage from './pages/VerifyEmailPage'
import DashboardPage from './pages/DashboardPage'
import LicensesPage from './pages/LicensesPage'
import LicenseDetailPage from './pages/LicenseDetailPage'
import AdminPage from './pages/AdminPage'
import SettingsPage from './pages/SettingsPage'
import Revenue from './pages/Revenue'
import ProductsPage from './pages/ProductsPage'

function PrivateRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuthStore()
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }
  
  return isAuthenticated ? children : <Navigate to="/login" />
}

function PublicRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuthStore()
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }
  
  return !isAuthenticated ? children : <Navigate to="/dashboard" />
}

function AdminRoute({ children }) {
  const { user, isAuthenticated, isLoading } = useAuthStore()
  
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }
  
  if (!isAuthenticated) return <Navigate to="/login" />
  if (!user?.is_admin) return <Navigate to="/dashboard" />
  
  return children
}

function App() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={
        <PublicRoute>
          <LoginPage />
        </PublicRoute>
      } />
      <Route path="/register" element={
        <PublicRoute>
          <RegisterPage />
        </PublicRoute>
      } />
      <Route path="/verify-email" element={<VerifyEmailPage />} />
      
      {/* Private Routes */}
      <Route path="/" element={
        <PrivateRoute>
          <Layout />
        </PrivateRoute>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardPage />} />
        <Route path="licenses" element={<LicensesPage />} />
        <Route path="licenses/:id" element={<LicenseDetailPage />} />
        <Route path="settings" element={<SettingsPage />} />
        <Route path="admin" element={
          <AdminRoute>
            <AdminPage />
          </AdminRoute>
        } />
        <Route path="revenue" element={
          <AdminRoute>
            <Revenue />
          </AdminRoute>
        } />
        <Route path="products" element={
          <AdminRoute>
            <ProductsPage />
          </AdminRoute>
        } />
      </Route>
      
      {/* Catch all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
