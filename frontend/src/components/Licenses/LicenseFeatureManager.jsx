import { useState, useEffect } from 'react'
import { Check, X, Loader2, Settings, Info } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../../utils/api'

export default function LicenseFeatureManager({ licenseId, onUpdate }) {
  const [features, setFeatures] = useState([])
  const [enabledFeatures, setEnabledFeatures] = useState([])
  const [loading, setLoading] = useState(true)
  const [updating, setUpdating] = useState(null)

  useEffect(() => {
    fetchFeatures()
  }, [licenseId])

  const fetchFeatures = async () => {
    try {
      setLoading(true)
      const response = await api.get(`/licenses/${licenseId}/features`)
      setFeatures(response.data.available_features || [])
      setEnabledFeatures(response.data.enabled_features || [])
    } catch (err) {
      console.error('Failed to load features', err)
      toast.error('Fehler beim Laden der Features')
    } finally {
      setLoading(false)
    }
  }

  const toggleFeature = async (featureSlug, currentlyEnabled) => {
    setUpdating(featureSlug)
    try {
      await api.patch(`/licenses/${licenseId}/features`, {
        feature_slug: featureSlug,
        enabled: !currentlyEnabled
      })
      
      // Update local state
      if (currentlyEnabled) {
        setEnabledFeatures(prev => prev.filter(f => f.toLowerCase() !== featureSlug.toLowerCase()))
      } else {
        setEnabledFeatures(prev => [...prev, featureSlug])
      }
      
      toast.success(`Feature "${featureSlug}" ${!currentlyEnabled ? 'aktiviert' : 'deaktiviert'}`)
      
      if (onUpdate) onUpdate()
    } catch (err) {
      console.error('Failed to toggle feature', err)
      toast.error(err.response?.data?.detail || 'Fehler beim Ändern des Features')
    } finally {
      setUpdating(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center p-6">
        <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
      </div>
    )
  }

  if (features.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500 dark:text-gray-400">
        <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Keine Features für dieses Produkt verfügbar.</p>
        <p className="text-xs mt-1">Fügen Sie zuerst Features zum Produkt hinzu.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-4">
        <Settings className="w-4 h-4 text-gray-500" />
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Feature-Verwaltung
        </h4>
      </div>
      
      <div className="space-y-2">
        {features.map((feature) => {
          const isEnabled = enabledFeatures.some(
            f => f.toLowerCase() === feature.slug.toLowerCase()
          )
          const isUpdating = updating === feature.slug
          
          return (
            <div
              key={feature.slug}
              className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                isEnabled
                  ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800'
                  : 'bg-gray-50 border-gray-200 dark:bg-gray-800 dark:border-gray-700'
              }`}
            >
              <div className="flex-1 min-w-0 pr-4">
                <div className="flex items-center gap-2">
                  <span className={`font-medium text-sm ${
                    isEnabled 
                      ? 'text-green-700 dark:text-green-300' 
                      : 'text-gray-700 dark:text-gray-300'
                  }`}>
                    {feature.name}
                  </span>
                  <span className="text-xs px-1.5 py-0.5 rounded bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400 font-mono">
                    {feature.slug}
                  </span>
                </div>
                {feature.description && (
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {feature.description}
                  </p>
                )}
              </div>
              
              <button
                onClick={() => toggleFeature(feature.slug, isEnabled)}
                disabled={isUpdating}
                className={`relative w-12 h-6 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 ${
                  isEnabled
                    ? 'bg-green-500 focus:ring-green-500'
                    : 'bg-gray-300 dark:bg-gray-600 focus:ring-gray-500'
                } ${isUpdating ? 'opacity-50 cursor-wait' : 'cursor-pointer'}`}
              >
                {isUpdating ? (
                  <Loader2 className="w-4 h-4 absolute top-1 left-1 animate-spin text-white" />
                ) : (
                  <span
                    className={`absolute top-0.5 w-5 h-5 rounded-full bg-white shadow transition-transform ${
                      isEnabled ? 'translate-x-6' : 'translate-x-0.5'
                    }`}
                  />
                )}
              </button>
            </div>
          )
        })}
      </div>
      
      <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {enabledFeatures.length} von {features.length} Features aktiviert
        </p>
      </div>
    </div>
  )
}
