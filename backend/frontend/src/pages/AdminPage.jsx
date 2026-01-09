import { useEffect, useState } from 'react'
import { adminApi } from '../services/api'
import { Users, Key, Monitor, Activity, Shield, ShieldOff, UserCheck, UserX } from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

function StatCard({ icon: Icon, label, value, color }) {
  return (
    <div className="card p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{label}</p>
          <p className="mt-2 text-3xl font-semibold text-gray-900 dark:text-white">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  )
}

export default function AdminPage() {
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  
  useEffect(() => {
    loadData()
  }, [])
  
  const loadData = async () => {
    try {
      const [statsRes, usersRes] = await Promise.all([
        adminApi.getStats(),
        adminApi.listUsers(),
      ])
      setStats(statsRes.data)
      setUsers(usersRes.data.users)
    } catch (err) {
      toast.error('Fehler beim Laden der Admin-Daten')
    } finally {
      setIsLoading(false)
    }
  }
  
  const handleToggleAdmin = async (userId) => {
    try {
      const response = await adminApi.toggleAdmin(userId)
      setUsers(users.map(u => u.id === userId ? response.data : u))
      toast.success('Benutzer aktualisiert')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Aktualisieren')
    }
  }
  
  const handleToggleActive = async (userId) => {
    try {
      const response = await adminApi.toggleActive(userId)
      setUsers(users.map(u => u.id === userId ? response.data : u))
      toast.success('Benutzer aktualisiert')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Aktualisieren')
    }
  }
  
  const handleApproveUser = async (userId) => {
    try {
      const response = await adminApi.approveUser(userId)
      setUsers(users.map(u => u.id === userId ? response.data : u))
      toast.success('Benutzer freigegeben')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Freigeben')
    }
  }
  
  const handleRejectUser = async (userId) => {
    try {
      const response = await adminApi.rejectUser(userId)
      setUsers(users.map(u => u.id === userId ? response.data : u))
      toast.success('Benutzer abgelehnt')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Ablehnen')
    }
  }
  
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin-Übersicht</h1>
        <p className="text-gray-500 dark:text-gray-400">Systemübersicht und Benutzerverwaltung</p>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={Users}
          label="Benutzer gesamt"
          value={stats?.total_users || 0}
          color="bg-blue-600"
        />
        <StatCard
          icon={Key}
          label="Aktive Lizenzen"
          value={stats?.active_licenses || 0}
          color="bg-green-600"
        />
        <StatCard
          icon={Monitor}
          label="Aktive Geräte"
          value={stats?.active_devices || 0}
          color="bg-purple-600"
        />
        <StatCard
          icon={Activity}
          label="Validierungen gesamt"
          value={stats?.total_validations || 0}
          color="bg-orange-600"
        />
      </div>
      
      {/* Users Table */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Benutzer</h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Benutzer
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Rolle
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Registriert
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Aktionen
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {users.map(user => (
                <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">
                        {user.full_name || 'Kein Name'}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {user.email}
                      </p>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex flex-wrap items-center gap-1">
                      {user.is_active ? (
                        <span className="badge-success">Aktiv</span>
                      ) : (
                        <span className="badge-danger">Deaktiviert</span>
                      )}
                      {user.is_approved ? (
                        <span className="badge-info">Freigegeben</span>
                      ) : (
                        <span className="badge-warning">Ausstehend</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {user.is_admin ? (
                      <span className="badge bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                        Admin
                      </span>
                    ) : (
                      <span className="text-gray-500">Benutzer</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {format(new Date(user.created_at), 'dd.MM.yyyy')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      {!user.is_approved ? (
                        <button
                          onClick={() => handleApproveUser(user.id)}
                          className="p-2 rounded text-green-600 hover:bg-green-100 dark:hover:bg-green-900"
                          title="Benutzer freigeben"
                        >
                          <UserCheck className="w-4 h-4" />
                        </button>
                      ) : (
                        <button
                          onClick={() => handleRejectUser(user.id)}
                          className="p-2 rounded text-orange-600 hover:bg-orange-100 dark:hover:bg-orange-900"
                          title="Freigabe zurückziehen"
                        >
                          <UserX className="w-4 h-4" />
                        </button>
                      )}
                      <button
                        onClick={() => handleToggleAdmin(user.id)}
                        className={`p-2 rounded ${
                          user.is_admin 
                            ? 'text-purple-600 hover:bg-purple-100 dark:hover:bg-purple-900' 
                            : 'text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                        title={user.is_admin ? 'Admin-Rechte entfernen' : 'Zum Admin machen'}
                      >
                        {user.is_admin ? <ShieldOff className="w-4 h-4" /> : <Shield className="w-4 h-4" />}
                      </button>
                      <button
                        onClick={() => handleToggleActive(user.id)}
                        className={`px-2 py-1 text-xs rounded ${
                          user.is_active 
                            ? 'text-red-600 hover:bg-red-100 dark:hover:bg-red-900' 
                            : 'text-green-600 hover:bg-green-100 dark:hover:bg-green-900'
                        }`}
                        title={user.is_active ? 'Benutzer deaktivieren' : 'Benutzer aktivieren'}
                      >
                        {user.is_active ? 'Deaktivieren' : 'Aktivieren'}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
