import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useLicenseStore } from '../store/licenseStore'
import { useAuthStore } from '../store/authStore'
import { 
  ArrowLeft, Copy, Key, Monitor, Calendar, 
  Activity, Ban, Trash2, CheckCircle, XCircle,
  Plus, DollarSign
} from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'
import { revenueApi } from '../services/api'

function StatusBadge({ status }) {
  const styles = {
    active: 'badge-success',
    expired: 'badge-danger',
    revoked: 'badge-warning',
    blocked: 'badge-danger',
  }
  
  return (
    <span className={styles[status] || 'badge-info'}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </span>
  )
}

export default function LicenseDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const { 
    selectedLicense: license, 
    fetchLicense, 
    deleteLicense,
    revokeLicense,
    blockDevice,
    unblockDevice,
    deleteDevice,
    isLoading,
    clearSelected
  } = useLicenseStore()
  
  // Extension modal state
  const [showExtendModal, setShowExtendModal] = useState(false)
  const [extendDays, setExtendDays] = useState(30)
  const [extendAmount, setExtendAmount] = useState('')
  const [extendNotes, setExtendNotes] = useState('')
  const [extending, setExtending] = useState(false)
  
  useEffect(() => {
    fetchLicense(id)
    return () => clearSelected()
  }, [id])
  
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    toast.success('In die Zwischenablage kopiert!')
  }
  
  const handleDelete = async () => {
    if (confirm('Lizenz wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.')) {
      try {
        await deleteLicense(parseInt(id))
        toast.success('Lizenz gelöscht')
        navigate('/licenses')
      } catch (err) {
        toast.error('Fehler beim Löschen der Lizenz')
      }
    }
  }
  
  const handleRevoke = async () => {
    if (confirm('Lizenz wirklich widerrufen?')) {
      try {
        await revokeLicense(parseInt(id))
        toast.success('Lizenz widerrufen')
      } catch (err) {
        toast.error('Fehler beim Widerrufen der Lizenz')
      }
    }
  }
  
  const handleBlockDevice = async (deviceId) => {
    try {
      await blockDevice(deviceId)
      toast.success('Gerät gesperrt')
    } catch (err) {
      toast.error('Fehler beim Sperren des Geräts')
    }
  }
  
  const handleUnblockDevice = async (deviceId) => {
    try {
      await unblockDevice(deviceId)
      toast.success('Gerät entsperrt')
    } catch (err) {
      toast.error('Fehler beim Entsperren des Geräts')
    }
  }
  
  const handleDeleteDevice = async (deviceId) => {
    if (confirm('Gerät von der Lizenz entfernen?')) {
      try {
        await deleteDevice(deviceId)
        toast.success('Gerät entfernt')
      } catch (err) {
        toast.error('Fehler beim Entfernen des Geräts')
      }
    }
  }
  
  const handleExtendLicense = async () => {
    try {
      setExtending(true)
      const data = {
        days: extendDays,
        revenue: extendAmount ? {
          amount: parseFloat(extendAmount),
          currency: 'EUR',
          notes: extendNotes || null
        } : null
      }
      await revenueApi.extendLicense(parseInt(id), data)
      toast.success(`Lizenz um ${extendDays} Tage verlängert`)
      setShowExtendModal(false)
      setExtendDays(30)
      setExtendAmount('')
      setExtendNotes('')
      fetchLicense(id)
    } catch (err) {
      toast.error('Fehler beim Verlängern der Lizenz')
    } finally {
      setExtending(false)
    }
  }
  
  if (isLoading || !license) {
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
        <div className="flex items-center space-x-4">
          <Link
            to="/licenses"
            className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Lizenzdetails
            </h1>
            <p className="text-gray-500 dark:text-gray-400">
              {license.name || 'Unbenannte Lizenz'}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {user?.is_admin && (
            <button 
              onClick={() => setShowExtendModal(true)} 
              className="btn-primary"
            >
              <Plus className="w-4 h-4 mr-2" />
              Verlängern
            </button>
          )}
          {license.status === 'active' && (
            <button onClick={handleRevoke} className="btn-secondary">
              <Ban className="w-4 h-4 mr-2" />
              Widerrufen
            </button>
          )}
          <button onClick={handleDelete} className="btn-danger">
            <Trash2 className="w-4 h-4 mr-2" />
            Löschen
          </button>
        </div>
      </div>
      
      {/* License Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* License Key Card */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Lizenzschlüssel
            </h2>
            <div className="flex items-center space-x-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <Key className="w-5 h-5 text-gray-400" />
              <code className="flex-1 font-mono text-sm break-all">{license.key}</code>
              <button
                onClick={() => copyToClipboard(license.key)}
                className="p-2 text-gray-400 hover:text-primary-600"
              >
                <Copy className="w-5 h-5" />
              </button>
            </div>
          </div>
          
          {/* Devices */}
          <div className="card">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Geräte ({license.devices?.length || 0} / {license.max_devices === 0 ? '∞' : license.max_devices})
              </h2>
            </div>
            
            {!license.devices?.length ? (
              <div className="p-8 text-center">
                <Monitor className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">Noch keine Geräte registriert</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200 dark:divide-gray-700">
                {license.devices.map(device => (
                  <div key={device.id} className="p-4 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="p-2 bg-gray-100 dark:bg-gray-700 rounded-lg">
                        <Monitor className="w-5 h-5 text-gray-500" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white">
                          {device.device_name || 'Unbekanntes Gerät'}
                        </p>
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          {device.os} • {device.ip_address}
                        </p>
                        <p className="text-xs text-gray-400 font-mono">
                          {device.device_id.slice(0, 32)}...
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <StatusBadge status={device.status} />
                      <div className="flex items-center space-x-1">
                        {device.status === 'active' ? (
                          <button
                            onClick={() => handleBlockDevice(device.id)}
                            className="p-2 text-gray-400 hover:text-yellow-600"
                            title="Gerät sperren"
                          >
                            <Ban className="w-4 h-4" />
                          </button>
                        ) : (
                          <button
                            onClick={() => handleUnblockDevice(device.id)}
                            className="p-2 text-gray-400 hover:text-green-600"
                            title="Gerät entsperren"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => handleDeleteDevice(device.id)}
                          className="p-2 text-gray-400 hover:text-red-600"
                          title="Gerät entfernen"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Activity Log */}
          <div className="card">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                Aktivitätsprotokoll
              </h2>
            </div>
            
            {!license.activity?.length ? (
              <div className="p-8 text-center">
                <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">Noch keine Aktivität</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200 dark:divide-gray-700 max-h-96 overflow-y-auto">
                {license.activity.map(activity => (
                  <div key={activity.id} className="px-6 py-3 flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {activity.action === 'validated' && (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      )}
                      {activity.action === 'registered' && (
                        <Monitor className="w-4 h-4 text-blue-500" />
                      )}
                      <div>
                        <p className="text-sm text-gray-900 dark:text-white">
                          {activity.device_name || 'Unbekannt'} - {activity.action}
                        </p>
                        <p className="text-xs text-gray-500">{activity.ip_address}</p>
                      </div>
                    </div>
                    <span className="text-xs text-gray-400">
                      {format(new Date(activity.timestamp), 'MMM d, HH:mm')}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
        
        {/* Sidebar */}
        <div className="space-y-6">
          <div className="card p-6">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-4">
              Lizenzinformationen
            </h3>
            
            <dl className="space-y-4">
              <div>
                <dt className="text-xs text-gray-400">Status</dt>
                <dd className="mt-1">
                  <StatusBadge status={license.status} />
                </dd>
              </div>
              
              <div>
                <dt className="text-xs text-gray-400">Typ</dt>
                <dd className="mt-1 text-sm font-medium text-gray-900 dark:text-white capitalize">
                  {license.license_type}
                </dd>
              </div>
              
              <div>
                <dt className="text-xs text-gray-400">Max. Geräte</dt>
                <dd className="mt-1 text-sm font-medium text-gray-900 dark:text-white">
                  {license.max_devices === 0 ? 'Unbegrenzt' : license.max_devices}
                </dd>
              </div>
              
              <div>
                <dt className="text-xs text-gray-400">Läuft ab</dt>
                <dd className="mt-1 text-sm font-medium text-gray-900 dark:text-white">
                  {license.expires_at
                    ? format(new Date(license.expires_at), 'dd.MM.yyyy')
                    : 'Nie'}
                </dd>
              </div>
              
              {license.days_remaining !== null && (
                <div>
                  <dt className="text-xs text-gray-400">Verbleibende Tage</dt>
                  <dd className={`mt-1 text-sm font-medium ${
                    license.days_remaining <= 30 
                      ? 'text-yellow-600' 
                      : 'text-gray-900 dark:text-white'
                  }`}>
                    {license.days_remaining} Tage
                  </dd>
                </div>
              )}
              
              <div>
                <dt className="text-xs text-gray-400">Erstellt</dt>
                <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                  {format(new Date(license.created_at), 'dd.MM.yyyy HH:mm')}
                </dd>
              </div>
              
              <div>
                <dt className="text-xs text-gray-400">Zuletzt aktualisiert</dt>
                <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                  {format(new Date(license.updated_at), 'dd.MM.yyyy HH:mm')}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
      
      {/* Extend License Modal */}
      {showExtendModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full mx-4 p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Lizenz verlängern
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Tage verlängern *
                </label>
                <input
                  type="number"
                  value={extendDays}
                  onChange={(e) => setExtendDays(parseInt(e.target.value) || 1)}
                  min="1"
                  max="3650"
                  className="input"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Neues Ablaufdatum: {license.expires_at 
                    ? format(new Date(new Date(license.expires_at).getTime() + extendDays * 24 * 60 * 60 * 1000), 'dd.MM.yyyy')
                    : format(new Date(Date.now() + extendDays * 24 * 60 * 60 * 1000), 'dd.MM.yyyy')
                  }
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Einnahmen (optional)
                </label>
                <div className="relative">
                  <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="number"
                    value={extendAmount}
                    onChange={(e) => setExtendAmount(e.target.value)}
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                    className="input pl-10"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Leer lassen, wenn keine Einnahmen gebucht werden sollen
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Notizen (optional)
                </label>
                <textarea
                  value={extendNotes}
                  onChange={(e) => setExtendNotes(e.target.value)}
                  placeholder="z.B. Zahlungsmethode, Rechnungsnummer..."
                  rows={2}
                  className="input"
                />
              </div>
            </div>
            
            <div className="flex justify-end space-x-3 mt-6">
              <button
                onClick={() => setShowExtendModal(false)}
                className="btn-secondary"
                disabled={extending}
              >
                Abbrechen
              </button>
              <button
                onClick={handleExtendLicense}
                className="btn-primary"
                disabled={extending || extendDays < 1}
              >
                {extending ? 'Wird verlängert...' : 'Verlängern'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
