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
    toast.success('Lizenzschlüssel kopiert!')
  }
  
  const handleDelete = async (id) => {
    if (confirm('Lizenz wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.')) {
      try {
        await deleteLicense(id)
        toast.success('Lizenz gelöscht')
      } catch (err) {
        toast.error('Fehler beim Löschen')
      }
    }
  }
  
  const handleRevoke = async (id) => {
    if (confirm('Lizenz wirklich widerrufen?')) {
      try {
        await revokeLicense(id)
        toast.success('Lizenz widerrufen')
      } catch (err) {
        toast.error('Fehler beim Widerrufen')
      }
    }
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Lizenzen</h1>
          <p className="text-gray-500 dark:text-gray-400">Verwalte deine Software-Lizenzen</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="btn-primary whitespace-nowrap flex-shrink-0">
          <Plus className="w-4 h-4 mr-2" />
          Neue Lizenz
        </button>
      </div>
      
      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Suche nach Schlüssel oder Name..."
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
            <option value="all">Alle Typen</option>
            <option value="unlimited">Unbegrenzt</option>
            <option value="trial">Testversion</option>
            <option value="limited">Zeitlich</option>
          </select>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="input w-full md:w-40"
          >
            <option value="all">Alle Status</option>
            <option value="active">Aktiv</option>
            <option value="expired">Abgelaufen</option>
            <option value="revoked">Widerrufen</option>
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
                ? 'Keine Lizenzen gefunden'
                : 'Noch keine Lizenzen vorhanden'}
            </p>
            {!searchTerm && filterType === 'all' && filterStatus === 'all' && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 btn-primary"
              >
                Erste Lizenz erstellen
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[800px]">
              <thead className="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Lizenz
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Typ
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Geräte
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Läuft ab
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    Aktionen
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredLicenses.map(license => (
                  <tr key={license.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="flex items-center space-x-2">
                          <code 
                            className="font-mono text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded select-all cursor-pointer max-w-[200px] truncate block"
                            onClick={() => copyToClipboard(license.key)}
                            title={license.key}
                          >
                            {license.key}
                          </code>
                          <button
                            onClick={() => copyToClipboard(license.key)}
                            className="p-1 text-gray-400 hover:text-primary-600 dark:hover:text-primary-400 flex-shrink-0"
                            title="Copy full key"
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
                        ? format(new Date(license.expires_at), 'dd.MM.yyyy')
                        : 'Nie'}
                      {license.days_remaining !== null && license.days_remaining <= 30 && (
                        <span className="ml-2 text-yellow-600 dark:text-yellow-400">
                          (noch {license.days_remaining} Tage)
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <Link
                          to={`/licenses/${license.id}`}
                          className="p-2 text-gray-400 hover:text-primary-600"
                          title="Details anzeigen"
                        >
                          <Eye className="w-4 h-4" />
                        </Link>
                        {license.status === 'active' && (
                          <button
                            onClick={() => handleRevoke(license.id)}
                            className="p-2 text-gray-400 hover:text-yellow-600"
                            title="Widerrufen"
                          >
                            <Ban className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => handleDelete(license.id)}
                          className="p-2 text-gray-400 hover:text-red-600"
                          title="Löschen"
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
