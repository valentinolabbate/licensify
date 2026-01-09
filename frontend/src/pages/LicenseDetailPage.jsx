import { useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useLicenseStore } from '../store/licenseStore'
import { 
  ArrowLeft, Copy, Key, Monitor, Calendar, 
  Activity, Ban, Trash2, CheckCircle, XCircle 
} from 'lucide-react'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

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
  
  useEffect(() => {
    fetchLicense(id)
    return () => clearSelected()
  }, [id])
  
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard!')
  }
  
  const handleDelete = async () => {
    if (confirm('Are you sure you want to delete this license?')) {
      try {
        await deleteLicense(parseInt(id))
        toast.success('License deleted')
        navigate('/licenses')
      } catch (err) {
        toast.error('Failed to delete license')
      }
    }
  }
  
  const handleRevoke = async () => {
    if (confirm('Are you sure you want to revoke this license?')) {
      try {
        await revokeLicense(parseInt(id))
        toast.success('License revoked')
      } catch (err) {
        toast.error('Failed to revoke license')
      }
    }
  }
  
  const handleBlockDevice = async (deviceId) => {
    try {
      await blockDevice(deviceId)
      toast.success('Device blocked')
    } catch (err) {
      toast.error('Failed to block device')
    }
  }
  
  const handleUnblockDevice = async (deviceId) => {
    try {
      await unblockDevice(deviceId)
      toast.success('Device unblocked')
    } catch (err) {
      toast.error('Failed to unblock device')
    }
  }
  
  const handleDeleteDevice = async (deviceId) => {
    if (confirm('Remove this device from the license?')) {
      try {
        await deleteDevice(deviceId)
        toast.success('Device removed')
      } catch (err) {
        toast.error('Failed to remove device')
      }
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
              License Details
            </h1>
            <p className="text-gray-500 dark:text-gray-400">
              {license.name || 'Unnamed License'}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {license.status === 'active' && (
            <button onClick={handleRevoke} className="btn-secondary">
              <Ban className="w-4 h-4 mr-2" />
              Revoke
            </button>
          )}
          <button onClick={handleDelete} className="btn-danger">
            <Trash2 className="w-4 h-4 mr-2" />
            Delete
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
              License Key
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
                Devices ({license.devices?.length || 0} / {license.max_devices === 0 ? '∞' : license.max_devices})
              </h2>
            </div>
            
            {!license.devices?.length ? (
              <div className="p-8 text-center">
                <Monitor className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">No devices registered yet</p>
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
                          {device.device_name || 'Unknown Device'}
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
                            title="Block device"
                          >
                            <Ban className="w-4 h-4" />
                          </button>
                        ) : (
                          <button
                            onClick={() => handleUnblockDevice(device.id)}
                            className="p-2 text-gray-400 hover:text-green-600"
                            title="Unblock device"
                          >
                            <CheckCircle className="w-4 h-4" />
                          </button>
                        )}
                        <button
                          onClick={() => handleDeleteDevice(device.id)}
                          className="p-2 text-gray-400 hover:text-red-600"
                          title="Remove device"
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
                Activity Log
              </h2>
            </div>
            
            {!license.activity?.length ? (
              <div className="p-8 text-center">
                <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">No activity yet</p>
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
                          {activity.device_name || 'Unknown'} - {activity.action}
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
              License Information
            </h3>
            
            <dl className="space-y-4">
              <div>
                <dt className="text-xs text-gray-400">Status</dt>
                <dd className="mt-1">
                  <StatusBadge status={license.status} />
                </dd>
              </div>
              
              <div>
                <dt className="text-xs text-gray-400">Type</dt>
                <dd className="mt-1 text-sm font-medium text-gray-900 dark:text-white capitalize">
                  {license.license_type}
                </dd>
              </div>
              
              <div>
                <dt className="text-xs text-gray-400">Max Devices</dt>
                <dd className="mt-1 text-sm font-medium text-gray-900 dark:text-white">
                  {license.max_devices === 0 ? 'Unlimited' : license.max_devices}
                </dd>
              </div>
              
              <div>
                <dt className="text-xs text-gray-400">Expires</dt>
                <dd className="mt-1 text-sm font-medium text-gray-900 dark:text-white">
                  {license.expires_at
                    ? format(new Date(license.expires_at), 'MMM d, yyyy')
                    : 'Never'}
                </dd>
              </div>
              
              {license.days_remaining !== null && (
                <div>
                  <dt className="text-xs text-gray-400">Days Remaining</dt>
                  <dd className={`mt-1 text-sm font-medium ${
                    license.days_remaining <= 30 
                      ? 'text-yellow-600' 
                      : 'text-gray-900 dark:text-white'
                  }`}>
                    {license.days_remaining} days
                  </dd>
                </div>
              )}
              
              <div>
                <dt className="text-xs text-gray-400">Created</dt>
                <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                  {format(new Date(license.created_at), 'MMM d, yyyy HH:mm')}
                </dd>
              </div>
              
              <div>
                <dt className="text-xs text-gray-400">Last Updated</dt>
                <dd className="mt-1 text-sm text-gray-900 dark:text-white">
                  {format(new Date(license.updated_at), 'MMM d, yyyy HH:mm')}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </div>
  )
}
