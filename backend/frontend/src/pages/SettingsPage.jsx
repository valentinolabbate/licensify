import { useState } from 'react'
import { authApi } from '../services/api'
import { User, Lock, Key, Save } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import toast from 'react-hot-toast'

export default function SettingsPage() {
  const { user } = useAuthStore()
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  
  const handleChangePassword = async (e) => {
    e.preventDefault()
    
    if (newPassword !== confirmPassword) {
      toast.error('Die neuen Passwörter stimmen nicht überein')
      return
    }
    
    if (newPassword.length < 8) {
      toast.error('Das Passwort muss mindestens 8 Zeichen lang sein')
      return
    }
    
    setIsLoading(true)
    
    try {
      await authApi.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      })
      
      toast.success('Passwort erfolgreich geändert')
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Fehler beim Ändern des Passworts')
    } finally {
      setIsLoading(false)
    }
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Einstellungen</h1>
        <p className="text-gray-500 dark:text-gray-400">Verwalte deine Kontoeinstellungen</p>
      </div>
      
      {/* Profile Info */}
      <div className="card p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
            <User className="w-5 h-5 text-primary-600 dark:text-primary-400" />
          </div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Profilinformationen</h2>
        </div>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Email
            </label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="input bg-gray-50 dark:bg-gray-800 cursor-not-allowed"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Vollständiger Name
            </label>
            <input
              type="text"
              value={user?.full_name || 'Nicht angegeben'}
              disabled
              className="input bg-gray-50 dark:bg-gray-800 cursor-not-allowed"
            />
          </div>
          
          <div className="flex items-center space-x-4 text-sm">
            <span className={`px-2 py-1 rounded ${user?.is_admin ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}`}>
              {user?.is_admin ? 'Admin' : 'Benutzer'}
            </span>
            <span className={`px-2 py-1 rounded ${user?.is_approved ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'}`}>
              {user?.is_approved ? 'Freigegeben' : 'Freigabe ausstehend'}
            </span>
          </div>
        </div>
      </div>
      
      {/* Change Password */}
      <div className="card p-6">
        <div className="flex items-center space-x-3 mb-6">
          <div className="p-2 bg-orange-100 dark:bg-orange-900 rounded-lg">
            <Key className="w-5 h-5 text-orange-600 dark:text-orange-400" />
          </div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Passwort ändern</h2>
        </div>
        
        <form onSubmit={handleChangePassword} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Aktuelles Passwort
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
                className="input pl-10"
                placeholder="Aktuelles Passwort eingeben"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Neues Passwort
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={8}
                className="input pl-10"
                placeholder="Neues Passwort (mind. 8 Zeichen)"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Neues Passwort bestätigen
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Lock className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                className={`input pl-10 ${confirmPassword && newPassword !== confirmPassword ? 'border-red-500' : ''}`}
                placeholder="Neues Passwort bestätigen"
              />
            </div>
            {confirmPassword && newPassword !== confirmPassword && (
              <p className="text-sm text-red-500 mt-1">Passwörter stimmen nicht überein</p>
            )}
          </div>
          
          <button
            type="submit"
            disabled={isLoading || !currentPassword || !newPassword || newPassword !== confirmPassword}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <span className="flex items-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Wird geändert...
              </span>
            ) : (
              <span className="flex items-center">
                <Save className="w-4 h-4 mr-2" />
                Passwort ändern
              </span>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}
