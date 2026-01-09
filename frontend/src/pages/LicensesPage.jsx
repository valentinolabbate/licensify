import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useLicenseStore } from '../store/licenseStore'
import { Plus, Search, Key, Copy, Eye, Trash2, Ban } from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import CreateLicenseModal from '../components/Licenses/CreateLicenseModal'

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

function LicenseTypeBadge({ type }) {
  const typeStyles = {
    unlimited: 'badge-info',
    trial: 'badge-warning',
    limited: 'badge-success',
  }
  
  return (
    <span className={typeStyles[type] || 'badge-info'}>
      {type.charAt(0).toUpperCase() + type.slice(1)}
    </span>
  )
}

export default function LicensesPage() {
  const { licenses, fetchLicenses, deleteLicense, revokeLicense, isLoading } = useLicenseStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterStatus, setFilterStatus] = useState('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  
  useEffect(() => {
    fetchLicenses()
  }, [])
  
  const filteredLicenses = licenses.filter(license => {
    const matchesSearch = 
      license.key.toLowerCase().includes(searchTerm.toLowerCase()) ||
      license.name?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesType = filterType === 'all' || license.license_type === filterType
    const matchesStatus = filterStatus === 'all' || license.status === filterStatus
    
    return matchesSearch && matchesType && matchesStatus
  })
  
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    toast.success('License key copied!')
  }
  
  const handleDelete = async (id) => {
    if (confirm('Are you sure you want to delete this license? This action cannot be undone.')) {
      try {
        await deleteLicense(id)
        toast.success('License deleted')
      } catch (err) {
        toast.error('Failed to delete license')
      }
    }
  }
  
  const handleRevoke = async (id) => {
    if (confirm('Are you sure you want to revoke this license?')) {
      try {
        await revokeLicense(id)
        toast.success('License revoked')
      } catch (err) {
        toast.error('Failed to revoke license')
      }
    }
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Licenses</h1>
          <p className="text-gray-500 dark:text-gray-400">Manage your software licenses</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn-primary">
          <Plus className="w-4 h-4 mr-2" />
          Create License
        </button>
      </div>
      
      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by key or name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="input w-full md:w-40"
          >
            <option value="all">All Types</option>
            <option value="unlimited">Unlimited</option>
            <option value="trial">Trial</option>
            <option value="limited">Limited</option>
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="input w-full md:w-40"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
            <option value="revoked">Revoked</option>
          </select>
        </div>
      </div>
      
      {/* License List */}
      <div className="card">
        {isLoading && licenses.length === 0 ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : filteredLicenses.length === 0 ? (
          <div className="p-8 text-center">
            <Key className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-500 dark:text-gray-400">
              {searchTerm || filterType !== 'all' || filterStatus !== 'all'
                ? 'No licenses match your filters'
                : 'No licenses yet'}
            </p>
            {!searchTerm && filterType === 'all' && filterStatus === 'all' && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 btn-primary"
              >
                Create your first license
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    License
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
                    Expires
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredLicenses.map(license => (
                  <tr key={license.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="flex items-center space-x-2">
                          <span className="font-mono text-sm">
                            {license.key.slice(0, 20)}...
                          </span>
                          <button
                            onClick={() => copyToClipboard(license.key)}
                            className="p-1 text-gray-400 hover:text-gray-600"
                            title="Copy key"
                          >
                            <Copy className="w-4 h-4" />
                          </button>
                        </div>
                        {license.name && (
                          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                            {license.name}
                          </p>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <LicenseTypeBadge type={license.license_type} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <LicenseStatusBadge status={license.status} />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {license.current_devices} / {license.max_devices === 0 ? '∞' : license.max_devices}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {license.expires_at
                        ? format(new Date(license.expires_at), 'MMM d, yyyy')
                        : 'Never'}
                      {license.days_remaining !== null && license.days_remaining <= 30 && (
                        <span className="ml-2 text-yellow-600 dark:text-yellow-400">
                          ({license.days_remaining}d left)
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <Link
                          to={`/licenses/${license.id}`}
                          className="p-2 text-gray-400 hover:text-primary-600"
                          title="View details"
                        >
                          <Eye className="w-4 h-4" />
                        </Link>
                        {license.status === 'active' && (
                          <button
                            onClick={() => handleRevoke(license.id)}
                            className="p-2 text-gray-400 hover:text-yellow-600"
                            title="Revoke"
                          >
                            <Ban className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(license.id)}
                          className="p-2 text-gray-400 hover:text-red-600"
                          title="Delete"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      {/* Create License Modal */}
      {showCreateModal && (
        <CreateLicenseModal onClose={() => setShowCreateModal(false)} />
      )}
    </div>
  )
}
