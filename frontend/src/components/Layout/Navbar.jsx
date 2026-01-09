import { useAuthStore } from '../../store/authStore'
import { LogOut, User, Moon, Sun } from 'lucide-react'
import { useState, useEffect } from 'react'

export default function Navbar() {
  const { user, logout } = useAuthStore()
  const [darkMode, setDarkMode] = useState(false)
  
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])
  
  return (
    <nav className="fixed top-0 left-0 right-0 h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 z-50">
      <div className="h-full px-4 flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">L</span>
          </div>
          <span className="ml-3 text-xl font-semibold text-gray-900 dark:text-white">
            License Manager
          </span>
        </div>
        
        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Dark mode toggle */}
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </button>
          
          {/* User info */}
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-primary-600 dark:text-primary-400" />
            </div>
            <div className="hidden md:block">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {user?.full_name || user?.email}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {user?.is_admin ? 'Administrator' : 'User'}
              </p>
            </div>
          </div>
          
          {/* Logout button */}
          <button
            onClick={logout}
            className="p-2 text-gray-500 hover:text-red-600 dark:text-gray-400 dark:hover:text-red-400 transition-colors"
            title="Logout"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>
    </nav>
  )
}
