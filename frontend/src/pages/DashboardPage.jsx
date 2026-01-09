import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useLicenseStore } from '../store/licenseStore'
import { Key, Monitor, Activity, Plus, ArrowRight } from 'lucide-react'
import { format } from 'date-fns'

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

function LicenseStatusBadge({ status }) {
  const statusStyles = {
    active: 'badge-success',
    expired: 'badge-danger',
    revoked: 'badge-warning',
  }
  
  return (
    <span className={statusStyles[status] || 'badge-info'}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}

export default function DashboardPage() {
  const { licenses, fetchLicenses, isLoading } = useLicenseStore()
  
  useEffect(() => {
    fetchLicenses()
  }, [])
  
  const activeLicenses = licenses.filter(l => l.status === 'active').length
  const totalDevices = licenses.reduce((sum, l) => sum + (l.current_devices || 0), 0)
  const expiringLicenses = licenses.filter(l => {
    if (!l.days_remaining) return false
    return l.days_remaining <= 30
  })
  
  if (isLoading && licenses.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
          <p className="text-gray-500 dark:text-gray-400">Welcome to your License Manager</p>
        </div>
        <Link to="/licenses" className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          New License
        </Link>
      </div>
      
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          icon={Key}
          label="Total Licenses"
          value={licenses.length}
          color="bg-primary-600"
        />
        <StatCard
          icon={Activity}
          label="Active Licenses"
          value={activeLicenses}
          color="bg-green-600"
        />
        <StatCard
          icon={Monitor}
          label="Total Devices"
          value={totalDevices}
          color="bg-blue-600"
        />
      </div>
      
      {/* Recent Licenses */}
      <div className="card">
        <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Recent Licenses</h2>
          <Link to="/licenses" className="text-sm text-primary-600 hover:text-primary-700 flex items-center">
            View all
            <ArrowRight className="w-4 h-4 ml-1" />
          </Link>
        </div>
        
        {licenses.length === 0 ? (
          <div className="p-8 text-center">
            <Key className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">No licenses yet</p>
            <Link to="/licenses" className="mt-4 inline-block btn-primary">
              Create your first license
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    License Key
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Devices
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Created
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {licenses.slice(0, 5).map(license => (
                  <tr key={license.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link
                        to={`/licenses/${license.id}`}
                        className="font-mono text-sm text-primary-600 hover:text-primary-700"
                      >
                        {license.key.slice(0, 16)}...
                      </Link>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="capitalize">{license.license_type}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <LicenseStatusBadge status={license.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {license.current_devices} / {license.max_devices === 0 ? '∞' : license.max_devices}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {format(new Date(license.created_at), 'MMM d, yyyy')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      {/* Expiring Soon */}
      {expiringLicenses.length > 0 && (
        <div className="card border-yellow-200 dark:border-yellow-800">
          <div className="px-6 py-4 border-b border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20">
            <h2 className="text-lg font-semibold text-yellow-800 dark:text-yellow-200">
              ⚠️ Expiring Soon
            </h2>
          </div>
          <div className="p-6">
            <ul className="space-y-3">
              {expiringLicenses.map(license => (
                <li key={license.id} className="flex items-center justify-between">
                  <div>
                    <Link
                      to={`/licenses/${license.id}`}
                      className="font-mono text-sm text-primary-600 hover:text-primary-700"
                    >
                      {license.key.slice(0, 16)}...
                    </Link>
                    <span className="ml-2 text-sm text-gray-500">
                      {license.name && `(${license.name})`}
                    </span>
                  </div>
                  <span className="text-sm text-yellow-600 dark:text-yellow-400">
                    {license.days_remaining} days remaining
                  </span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
