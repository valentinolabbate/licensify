import { NavLink } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { 
  LayoutDashboard, 
  Key, 
  Users,
  Settings,
  DollarSign,
  Package
} from 'lucide-react'

const navItems = [
  { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/licenses', icon: Key, label: 'Lizenzen' },
  { path: '/settings', icon: Settings, label: 'Einstellungen' },
]

const adminItems = [
  { path: '/products', icon: Package, label: 'Produkte' },
  { path: '/admin', icon: Users, label: 'Benutzer' },
  { path: '/revenue', icon: DollarSign, label: 'Einnahmen' },
]

export default function Sidebar() {
  const { user } = useAuthStore()
  
  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700">
      <nav className="p-4 space-y-2">
        {navItems.map(({ path, icon: Icon, label }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                  : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
              }`
            }
          >
            <Icon className="w-5 h-5" />
            <span className="font-medium">{label}</span>
          </NavLink>
        ))}
        
        {user?.is_admin && (
          <>
            <div className="pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
              <p className="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                Admin
              </p>
            </div>
            {adminItems.map(({ path, icon: Icon, label }) => (
              <NavLink
                key={path}
                to={path}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                      : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700'
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span className="font-medium">{label}</span>
              </NavLink>
            ))}
          </>
        )}
      </nav>
    </aside>
  )
}
